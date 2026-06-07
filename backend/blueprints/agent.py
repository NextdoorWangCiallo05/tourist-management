import os
import re
from datetime import datetime, timedelta
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models import db, Application, TourGroup, Route, Participant, PaymentRecord
from .response import ok

agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# ─── 工具函数（AI 可调用的能力） ───────────────────────────────

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


def tool_get_application(application_no):
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


def tool_search_applications(name=''):
    q = Application.query.order_by(Application.created_at.desc())
    if name:
        q = q.filter(Application.responsible_name.contains(name))
    apps = q.limit(10).all()
    return [{
        'application_no': a.application_no, 'responsible_name': a.responsible_name,
        'status': a.status, 'created_at': a.created_at.strftime('%Y-%m-%d')
    } for a in apps]


def tool_get_stats():
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    pending = Application.query.filter_by(status='pending').count()
    completed = Application.query.filter_by(status='completed').count()
    cancelled = Application.query.filter_by(status='cancelled').count()
    return {
        'total_applications': Application.query.count(),
        'total_groups': TourGroup.query.count(),
        'pending': pending, 'completed': completed, 'cancelled': cancelled,
        'today_new': Application.query.filter(db.func.date(Application.created_at) == today).count()
    }


def tool_calculate_fee(days_before, total_amount):
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
    # 异常2：出发日期已过仍未取消的未完成申请
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


# ─── 规则引擎（无需 API Key 即可运行） ────────────────────────

def parse_with_rules(msg):
    msg_lower = msg.lower()

    # 查询旅游团
    m = re.search(r'(?:搜索|查找|查|找|看看|有没有)(?:去|到)?(.{1,10})?[的]?(?:旅游团|团|路线|线路)', msg)
    if m:
        keyword = m.group(1) or ''
        groups = tool_search_groups(keyword=keyword)
        if not groups:
            return f'没有找到"{keyword}"相关的旅游团。'
        lines = [f'找到 {len(groups)} 个旅游团：']
        for g in groups[:5]:
            lines.append(f'  · {g["route_name"]}（{g["departure_date"]}）成人¥{g["adult_price"]} 余{g["remaining"]}/{g["max_capacity"]}人')
        return '\n'.join(lines)

    # 查询申请
    m = re.search(r'(?:搜索|查找|查|找|看看)(?:编号|申请)?\s*([A-Z0-9]{6,})', msg)
    if m:
        no = m.group(1)
        if not no.startswith('AP'):
            no = 'AP' + no
        app = tool_get_application(no)
        if not app:
            return f'没有找到申请编号为 {no} 的申请。'
        status_map = {'pending': '处理中', 'completed': '已完成', 'cancelled': '已取消'}
        deposit_status = '✅ 已付' if app['deposit_paid'] else '❌ 未付'
        return (
            f'申请 {app["application_no"]} 详情：\n'
            f'  · 路线：{app["route_name"]}\n'
            f'  · 责任人：{app["responsible_name"]}\n'
            f'  · 状态：{status_map.get(app["status"], app["status"])}\n'
            f'  · 人数：{app["adult_count"]}大{app["child_count"]}小\n'
            f'  · 订金：¥{app["deposit_amount"]} {deposit_status}\n'
            f'  · 余款：¥{app["balance_amount"]}\n'
            f'  · 出发：{app["departure_date"]}'
        )

    # 查某人的申请
    for prefix in ['王', '李', '张', '刘', '陈', '赵']:
        m = re.search(rf'({prefix}\w+)[的]?(?:申请|订单|报名)', msg)
        if m:
            name = m.group(1).rstrip('的')
            apps = tool_search_applications(name=name)
            if not apps:
                return f'没有找到 {name} 的申请记录。'
            lines = [f'{name} 的申请（共 {len(apps)} 条）：']
            status_map = {'pending': '处理中', 'completed': '已完成', 'cancelled': '已取消'}
            for a in apps:
                lines.append(f'  · {a["application_no"]} {status_map.get(a["status"], a["status"])} {a["created_at"]}')
            return '\n'.join(lines)

    # 查统计/概况
    if any(kw in msg for kw in ['统计', '概览', '概况', '总', '多少', '几个']):
        stats = tool_get_stats()
        return (
            f'📊 系统概览\n'
            f'  · 申请总数：{stats["total_applications"]}\n'
            f'  · 处理中：{stats["pending"]} / 已完成：{stats["completed"]} / 已取消：{stats["cancelled"]}\n'
            f'  · 旅游团：{stats["total_groups"]} 个\n'
            f'  · 今日新增：{stats["today_new"]} 条'
        )

    # 查异常/告警
    if any(kw in msg for kw in ['异常', '告警', '预警', '问题', '提醒', '待办']):
        alerts = tool_check_anomalies()
        if not alerts:
            return '✅ 系统运行正常，未发现异常。'
        lines = [f'发现 {len(alerts)} 个异常：']
        for a in alerts:
            icon = {'warning': '⚠️', 'danger': '🔴', 'info': 'ℹ️'}.get(a['type'], '📌')
            lines.append(f'  {icon} {a["title"]}')
            lines.append(f'    {a["detail"]}')
        return '\n'.join(lines)

    # 算手续费 — 带天数
    m = re.search(r'(?:取消|退)(?:订|单|款|费).*?(\d+)\s*天', msg)
    if m:
        days = int(m.group(1))
        fee = tool_calculate_fee(days, 1000)
        return (
            f'距出发 {days} 天取消：\n'
            f'  · 手续费率：{fee["rate"]}\n'
            f'  · 每 ¥1000 扣 ¥{fee["fee"]}，退 ¥{fee["refund"]}'
        )

    # 算手续费 — 通用咨询
    if any(kw in msg for kw in ['取消', '手续费', '退款', '退费']):
        return (
            '取消手续费规则：\n'
            '  · ≥ 出发前 30 天：免费取消\n'
            '  · ≥ 出发前 10 天：扣 20%\n'
            '  · ≥ 出发前 1 天：扣 50%\n'
            '  · 当天取消：扣 100%'
        )

    return None


# ─── Agent API ────────────────────────────────────────────────

@agent_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    msg = (data.get('message') or '').strip()
    if not msg:
        return ok({'reply': '请说点什么吧！试试"查旅游团"、"申请统计"、"异常检测"。'})

    # 先走规则引擎
    reply = parse_with_rules(msg)
    if reply:
        return ok({'reply': reply, 'mode': 'rule'})

    # 规则引擎没命中 → 走 LLM（如果配置了 API Key）
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': f'你是智游云管系统的AI助手。当前时间：{now}。请简洁回答旅游业务相关问题。'},
                    {'role': 'user', 'content': msg}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return ok({'reply': resp.choices[0].message.content, 'mode': 'llm'})
        except Exception as e:
            return ok({'reply': f'AI 回答失败（{str(e)}）', 'mode': 'error'})

    return ok({
        'reply': (
            '抱歉，我没有完全理解您的问题。\n\n'
            '您可以试试这样问：\n'
            '  · "查旅游团" — 查看可报名的旅游团\n'
            '  · "去云南的旅游团" — 搜索指定路线\n'
            '  · "查申请 AP12345678" — 查询申请详情\n'
            '  · "张伟的申请" — 按责任人查询\n'
            '  · "系统概览" — 查看统计数据\n'
            '  · "异常检测" — 检查系统异常\n'
            '  · "取消手续费怎么算" — 了解规则'
        ),
        'mode': 'fallback'
    })


@agent_bp.route('/anomalies', methods=['GET'])
@jwt_required()
def anomalies():
    return ok(tool_check_anomalies())
