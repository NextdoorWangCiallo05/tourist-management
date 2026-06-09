import os
import re
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, Response, stream_with_context
from flask_jwt_extended import jwt_required
from models import db, Application, TourGroup, Route, Participant, PaymentRecord
from .response import ok

agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# ═══════════════════════════════════════════════════════════════
# TOOLS — AI 可调用的能力（Function Calling 架构）
# ═══════════════════════════════════════════════════════════════

TOOLS = {}  # name -> {fn, schema}


def register_tool(name, schema):
    """注册工具函数"""
    def decorator(fn):
        TOOLS[name] = {'fn': fn, 'schema': schema}
        return fn
    return decorator


@register_tool('search_groups', {
    'description': '搜索可报名的旅游团',
    'parameters': {
        'keyword': {'type': 'string', 'description': '路线名称关键词，如"云南""大理"'},
        'date_from': {'type': 'string', 'description': '出发日期起 YYYY-MM-DD'},
        'date_to': {'type': 'string', 'description': '出发日期止 YYYY-MM-DD'},
    }
})
def tool_search_groups(keyword='', date_from='', date_to=''):
    q = TourGroup.query.filter_by(is_public=True)
    if keyword:
        routes = Route.query.filter(Route.route_name.contains(keyword)).all()
        route_ids = [r.id for r in routes]
        q = q.filter(TourGroup.route_id.in_(route_ids)) if route_ids else q
    if date_from:
        q = q.filter(TourGroup.departure_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        q = q.filter(TourGroup.departure_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    groups = q.all()
    result = []
    for g in groups:
        rt = Route.query.get(g.route_id)
        apps = [a for a in g.applications if a.status in ('pending', 'completed')]
        used = sum(a.adult_count + a.child_count for a in apps)
        result.append({
            'group_code': g.group_code, 'route_name': rt.route_name,
            'departure_date': str(g.departure_date), 'adult_price': g.adult_price,
            'remaining': max(0, g.max_capacity - used), 'max_capacity': g.max_capacity
        })
    return result


@register_tool('get_application', {
    'description': '查询申请详情',
    'parameters': {
        'application_no': {'type': 'string', 'description': '申请编号，如 APXXXXXXXX'},
    }
})
def tool_get_application(application_no):
    if not application_no.startswith('AP'):
        application_no = 'AP' + application_no
    a = Application.query.filter_by(application_no=application_no).first()
    if not a:
        return None
    g = TourGroup.query.get(a.tour_group_id)
    rt = Route.query.get(g.route_id)
    return {
        'application_no': a.application_no, 'route_name': rt.route_name,
        'responsible_name': a.responsible_name, 'status': a.status,
        'adult_count': a.adult_count, 'child_count': a.child_count,
        'deposit_amount': a.deposit_amount, 'deposit_paid': a.deposit_paid,
        'balance_amount': a.balance_amount, 'balance_paid': a.balance_paid,
        'departure_date': str(g.departure_date)
    }


@register_tool('search_applications', {
    'description': '按责任人名称搜索申请',
    'parameters': {
        'name': {'type': 'string', 'description': '责任人姓名'},
    }
})
def tool_search_applications(name=''):
    q = Application.query.order_by(Application.created_at.desc())
    if name:
        q = q.filter(Application.responsible_name.contains(name))
    apps = q.limit(10).all()
    status_map = {'pending': '处理中', 'completed': '已完成', 'cancelled': '已取消'}
    return [{
        'application_no': a.application_no, 'responsible_name': a.responsible_name,
        'status': status_map.get(a.status, a.status), 'created_at': a.created_at.strftime('%Y-%m-%d')
    } for a in apps]


@register_tool('get_stats', {
    'description': '获取系统统计数据概览',
    'parameters': {}
})
def tool_get_stats():
    today = datetime.now().date()
    pending = Application.query.filter_by(status='pending').count()
    completed = Application.query.filter_by(status='completed').count()
    cancelled = Application.query.filter_by(status='cancelled').count()
    return {
        'total_applications': Application.query.count(),
        'total_groups': TourGroup.query.count(),
        'pending': pending, 'completed': completed, 'cancelled': cancelled,
        'today_new': Application.query.filter(
            db.func.date(Application.created_at) == today
        ).count()
    }


@register_tool('calculate_fee', {
    'description': '计算取消手续费',
    'parameters': {
        'days_before': {'type': 'number', 'description': '距出发天数'},
        'total_amount': {'type': 'number', 'description': '总金额'},
    }
})
def tool_calculate_fee(days_before, total_amount=1000):
    if days_before >= 30:
        return {'fee': 0, 'refund': total_amount, 'rate': '0%'}
    elif days_before >= 10:
        fee = round(total_amount * 0.2, 2)
        return {'fee': fee, 'refund': round(total_amount - fee, 2), 'rate': '20%'}
    elif days_before >= 1:
        fee = round(total_amount * 0.5, 2)
        return {'fee': fee, 'refund': round(total_amount - fee, 2), 'rate': '50%'}
    else:
        return {'fee': total_amount, 'refund': 0, 'rate': '100%'}


@register_tool('check_anomalies', {
    'description': '检测系统异常告警（订金超期未完成、出发过期、名额将满）',
    'parameters': {}
})
def tool_check_anomalies():
    today = datetime.now().date()
    alerts = []
    # 异常1：订金已付但超过7天未完成
    unpaid = Application.query.filter(
        Application.deposit_paid == True,
        Application.status == 'pending',
        Application.created_at < datetime.now() - timedelta(days=7)
    ).all()
    for a in unpaid:
        alerts.append({
            'type': 'warning', 'module': '申请',
            'title': f'申请 {a.application_no} 订金已付但长期未完成',
            'detail': f'责任人 {a.responsible_name}，已等待 {(datetime.now() - a.created_at).days} 天'
        })
    # 异常2：出发日期已过仍未取消
    expired = Application.query.filter(
        Application.status.in_(['pending']),
        Application.tour_group_id.in_(
            db.session.query(TourGroup.id).filter(TourGroup.departure_date < today)
        )
    ).all()
    for a in expired:
        g = TourGroup.query.get(a.tour_group_id)
        alerts.append({
            'type': 'danger', 'module': '申请',
            'title': f'申请 {a.application_no} 已过出发日期未处理',
            'detail': f'旅游团 {g.group_code} 出发日期 {g.departure_date}'
        })
    # 异常3：人数快满的旅游团
    groups = TourGroup.query.all()
    for g in groups:
        apps = [a for a in g.applications if a.status in ('pending', 'completed')]
        used = sum(a.adult_count + a.child_count for a in apps)
        ratio = used / g.max_capacity if g.max_capacity > 0 else 0
        if ratio >= 0.85:
            rt = Route.query.get(g.route_id)
            alerts.append({
                'type': 'info', 'module': '旅游团',
                'title': f'{rt.route_name} 名额仅剩 {g.max_capacity - used} 个',
                'detail': f'已占用 {used}/{g.max_capacity}（{int(ratio*100)}%）'
            })
    return alerts


@register_tool('get_participants', {
    'description': '查询申请的参加者列表',
    'parameters': {
        'application_no': {'type': 'string', 'description': '申请编号'},
    }
})
def tool_get_participants(application_no):
    if not application_no.startswith('AP'):
        application_no = 'AP' + application_no
    a = Application.query.filter_by(application_no=application_no).first()
    if not a:
        return None
    participants = Participant.query.filter_by(application_id=a.id).all()
    return [{
        'name': p.name, 'id_type': p.id_type, 'is_adult': p.is_adult,
        'is_responsible': p.is_responsible, 'status': p.status
    } for p in participants]


# ═══════════════════════════════════════════════════════════════
# NLU 规则引擎（增强版正则匹配）
# ═══════════════════════════════════════════════════════════════

def parse_intent(msg):
    """基于增强正则的意图识别，返回 tool_name + params"""

    # ── 查旅游团 ──────────────────────────────────────────
    # "查旅游团" "看看云南有什么团" "搜索去大理的旅游团"
    m = re.search(r'(?:搜索|查找|查|找|看看|有没有|推荐|有什么)\s*(?:去|到|往)?(.{1,10})?[的]?(?:旅游团|旅行团|团|路线|线路|行程)', msg)
    if m:
        keyword = (m.group(1) or '').strip()
        return ('search_groups', {'keyword': keyword})

    # ── 查申请详情 ────────────────────────────────────────
    # "查申请 AP12345678" "申请编号AP12345678" "看看AP12345678"
    m = re.search(r'(?:申请编号|申请号|编号)?\s*([A-Za-z]{2}\d{4,}[A-Za-z0-9]*|AP[A-Z0-9]{8})', msg)
    if m:
        return ('get_application', {'application_no': m.group(1).upper()})

    # ── 查某人申请 ────────────────────────────────────────
    # "张三的申请" "查一下张三的订单" "张伟的报名"
    m = re.search(r'([\u4e00-\u9fa5]{2,4})[的]?(?:申请|订单|报名|记录)', msg)
    if m:
        return ('search_applications', {'name': m.group(1)})

    # ── 查统计/概览 ──────────────────────────────────────
    # "系统概览" "统计" "总共有多少申请"
    if any(kw in msg for kw in ['统计', '概览', '概况', '总共有', '有多少']):
        return ('get_stats', {})

    # ── 异常检测 ──────────────────────────────────────────
    # "异常检测" "有没有异常" "告警" "问题"
    if any(kw in msg for kw in ['异常', '告警', '预警', '问题', '待办', '提醒']):
        return ('check_anomalies', {})

    # ── 算手续费（带天数）─────────────────────────────────
    # "出发前20天取消扣多少" "提前15天退订"
    m = re.search(r'(?:取消|退|退款|手续费).*?(\d+)\s*天', msg)
    if m:
        return ('calculate_fee', {'days_before': int(m.group(1))})

    # ── 手续费规则 ────────────────────────────────────────
    # "取消规则" "手续费怎么算" "退款规则"
    if any(kw in msg for kw in ['取消', '手续费', '退款', '退费', '规则']):
        return ('calculate_fee', {'days_before': 30})

    # ── 查参加者 ──────────────────────────────────────────
    # "参加者AP12345678" "谁参加了"
    m = re.search(r'(?:参加者|参与者|谁参加了)\s*([A-Za-z]{2}\d{4,}[A-Za-z0-9]*|AP[A-Z0-9]{8})', msg)
    if m:
        return ('get_participants', {'application_no': m.group(1).upper()})

    return None, None


def execute_tool(name, params):
    """调用已注册的工具函数"""
    tool = TOOLS.get(name)
    if not tool:
        return None
    result = tool['fn'](**params)
    # 保存天数用于格式化
    if name == 'calculate_fee' and 'days_before' in params:
        tool_calculate_fee._last_days = params['days_before']
    return result


# ═══════════════════════════════════════════════════════════════
# 格式器 — 将工具返回的结构化数据转为人类可读文本
# ═══════════════════════════════════════════════════════════════

def format_result(name, data):
    if not data:
        return '未找到相关信息。'

    if name == 'search_groups':
        if not data:
            return '没有找到符合条件的旅游团。'
        lines = [f'找到 **{len(data)}** 个旅游团：']
        for g in data[:5]:
            lines.append(f'| {g["route_name"]} | {g["departure_date"]} | ¥{g["adult_price"]} | 余 {g["remaining"]}/{g["max_capacity"]} 人 |')
        return '\n'.join(lines)

    if name == 'get_application':
        status_map = {'pending': '处理中', 'completed': '已完成', 'cancelled': '已取消'}
        deposit_status = '✅ 已付' if data['deposit_paid'] else '❌ 未付'
        return (
            f'**申请 {data["application_no"]}** 详情：\n'
            f'  · 路线：{data["route_name"]}\n'
            f'  · 责任人：{data["responsible_name"]}\n'
            f'  · 状态：{status_map.get(data["status"], data["status"])}\n'
            f'  · 人数：{data["adult_count"]} 大 {data["child_count"]} 小\n'
            f'  · 订金：¥{data["deposit_amount"]} {deposit_status}\n'
            f'  · 余款：¥{data["balance_amount"]}\n'
            f'  · 出发：{data["departure_date"]}'
        )

    if name == 'search_applications':
        if not data:
            return '没有找到申请记录。'
        lines = [f'共 **{len(data)}** 条申请：']
        for a in data:
            lines.append(f'  · {a["application_no"]} — {a["status"]}（{a["created_at"]}）')
        return '\n'.join(lines)

    if name == 'get_stats':
        return (
            f'📊 **系统概览**\n'
            f'  · 申请总数：{data["total_applications"]}\n'
            f'  · 处理中：{data["pending"]} / 已完成：{data["completed"]} / 已取消：{data["cancelled"]}\n'
            f'  · 旅游团：{data["total_groups"]} 个\n'
            f'  · 今日新增：{data["today_new"]} 条'
        )

    if name == 'calculate_fee':
        if data['rate'] == '0%':
            return (
                f'**取消手续费规则：**\n'
                f'  · ≥ 出发前 30 天：**免费取消**\n'
                f'  · ≥ 出发前 10 天：扣 20%\n'
                f'  · ≥ 出发前 1 天：扣 50%\n'
                f'  · 当天取消：扣 100%'
            )
        days_val = getattr(calculate_fee, '_last_days', 30)
        return (
            f'距出发 {days_val} 天取消：\n'
            f'  · 手续费率：{data["rate"]}\n'
            f'  · 每 ¥1000 扣 ¥{data["fee"]}，退 ¥{data["refund"]}'
        )

    if name == 'check_anomalies':
        if not data:
            return '✅ **系统运行正常**，未发现异常。'
        lines = [f'发现 **{len(data)}** 个异常：']
        icons = {'warning': '⚠️', 'danger': '🔴', 'info': 'ℹ️'}
        for a in data:
            lines.append(f'  {icons.get(a["type"], "📌")} {a["title"]}')
            lines.append(f'    {a["detail"]}')
        return '\n'.join(lines)

    if name == 'get_participants':
        if not data:
            return '该申请没有参加者。'
        lines = [f'**{len(data)}** 名参加者：']
        for p in data:
            role = '(责任人)' if p['is_responsible'] else ''
            lines.append(f'  · {p["name"]} {role}')
        return '\n'.join(lines)

    return str(data)


# ═══════════════════════════════════════════════════════════════
# Chat API — 规则引擎 + GPT Function Calling
# ═══════════════════════════════════════════════════════════════

@agent_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    msg = (data.get('message') or '').strip()
    context = data.get('context', [])

    if not msg:
        return ok({'reply': '请说点什么吧！试试"查旅游团"、"系统概览"、"异常检测"。'})

    # 1. NLU 规则引擎
    tool_name, params = parse_intent(msg)
    if tool_name:
        result = execute_tool(tool_name, params)
        reply = format_result(tool_name, result)
        return ok({'reply': reply, 'mode': 'rule'})

    # 2. Function Calling — GPT 选择工具
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            # 构建 tools 定义
            openai_tools = []
            for name, tool in TOOLS.items():
                schema = tool['schema']
                props = {}
                for pname, pinfo in schema['parameters'].items():
                    props[pname] = {'type': pinfo.get('type', 'string'), 'description': pinfo.get('description', '')}
                openai_tools.append({
                    'type': 'function',
                    'function': {
                        'name': name,
                        'description': schema['description'],
                        'parameters': {'type': 'object', 'properties': props}
                    }
                })

            sys_msg = f'你是智游云管系统的 AI 助手。当前时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}。请根据用户问题调用合适的工具。如果工具返回的数据可以直接回答用户，请用中文简洁回复。'

            msgs = [{'role': 'system', 'content': sys_msg}]
            # 添加上下文
            for ctx in context[-6:]:
                msgs.append({'role': ctx['role'], 'content': ctx['content']})
            msgs.append({'role': 'user', 'content': msg})

            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=msgs,
                tools=openai_tools,
                tool_choice='auto',
                max_tokens=500,
                temperature=0.7
            )
            choice = resp.choices[0]

            if choice.finish_reason == 'tool_calls' and choice.message.tool_calls:
                # GPT 选择调用某个工具
                tc = choice.message.tool_calls[0]
                fn_name = tc.function.name
                try:
                    fn_params = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    fn_params = {}
                result = execute_tool(fn_name, fn_params)
                reply = format_result(fn_name, result)
                return ok({'reply': reply, 'mode': 'function_call'})
            else:
                return ok({'reply': choice.message.content or '暂无回复', 'mode': 'llm'})

        except Exception as e:
            return ok({'reply': f'AI 回答失败（{str(e)}）', 'mode': 'error'})

    # 3. Fallback
    return ok({
        'reply': (
            '抱歉，我没有完全理解您的问题。\n\n'
            '您可以试试这样问：\n'
            '  · "查旅游团" — 查看可报名的旅游团\n'
            '  · "去云南的旅游团" — 搜索指定路线\n'
            '  · "查申请 AP12345678" — 查询申请详情\n'
            '  · "张三的申请" — 按责任人查询\n'
            '  · "系统概览" — 查看统计数据\n'
            '  · "异常检测" — 检查系统异常\n'
            '  · "取消手续费怎么算" — 了解规则'
        ),
        'mode': 'fallback'
    })


# ═══════════════════════════════════════════════════════════════
# SSE 流式响应（GPT 模式逐字输出）
# ═══════════════════════════════════════════════════════════════

@agent_bp.route('/chat/stream', methods=['POST'])
@jwt_required()
def chat_stream():
    data = request.get_json()
    msg = (data.get('message') or '').strip()

    if not msg:
        return ok({'reply': '请输入消息'})

    # 先走规则引擎（非流式）
    tool_name, params = parse_intent(msg)
    if tool_name:
        result = execute_tool(tool_name, params)
        reply = format_result(tool_name, result)
        return Response(
            f'data: {json.dumps({"chunk": reply, "done": True, "mode": "rule"})}\n\n',
            mimetype='text/event-stream',
            headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
        )

    # GPT 流式
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        return Response(
            f'data: {json.dumps({"chunk": "需要配置 OPENAI_API_KEY 才能使用 GPT 流式回答。", "done": True, "mode": "error"})}\n\n',
            mimetype='text/event-stream'
        )

    def generate():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            sys_msg = f'你是智游云管系统的AI助手。当前时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}。请简洁回答。'
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': sys_msg},
                    {'role': 'user', 'content': msg}
                ],
                max_tokens=500,
                temperature=0.7,
                stream=True
            )
            for chunk in resp:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield f'data: {json.dumps({"chunk": delta.content, "done": False, "mode": "stream"})}\n\n'
            yield f'data: {json.dumps({"chunk": "", "done": True, "mode": "stream"})}\n\n'
        except Exception as e:
            yield f'data: {json.dumps({"chunk": f"AI 回答失败（{str(e)}）", "done": True, "mode": "error"})}\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@agent_bp.route('/anomalies', methods=['GET'])
@jwt_required()
def anomalies():
    return ok(tool_check_anomalies())
