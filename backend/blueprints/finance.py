from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from models import db, Application, Participant, PaymentRecord, TourGroup, Route, AuditLog
from .response import ok, not_found
import io as pyio
import csv

finance_bp = Blueprint('finance', __name__, url_prefix='/api')


@finance_bp.route('/daily_export', methods=['GET'])
@jwt_required()
def daily_export():
    ds = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    td = datetime.strptime(ds, '%Y-%m-%d')
    st = datetime(td.year, td.month, td.day, 0, 0, 0)
    et = datetime(td.year, td.month, td.day, 23, 59, 59)
    payments = PaymentRecord.query.filter(PaymentRecord.paid_at >= st, PaymentRecord.paid_at <= et).all()
    data = []
    for p in payments:
        a = Application.query.get(p.application_id)
        g = TourGroup.query.get(a.tour_group_id)
        rt = Route.query.get(g.route_id)
        data.append({'payment_id': p.id, 'application_no': a.application_no, 'route_name': rt.route_name,
                     'group_code': g.group_code, 'responsible_name': a.responsible_name,
                     'payment_type': p.payment_type, 'amount': p.amount,
                     'paid_at': p.paid_at.strftime('%Y-%m-%d %H:%M:%S')})
    return ok(data)


@finance_bp.route('/daily_export/excel', methods=['GET'])
@jwt_required()
def export_excel():
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = '财务导出'
    headers = ['支付ID', '申请编号', '路线名称', '旅游团', '责任人', '支付类型', '金额', '支付时间']
    ws.append(headers)
    ds = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    td = datetime.strptime(ds, '%Y-%m-%d')
    st = datetime(td.year, td.month, td.day, 0, 0, 0)
    et = datetime(td.year, td.month, td.day, 23, 59, 59)
    payments = PaymentRecord.query.filter(PaymentRecord.paid_at >= st, PaymentRecord.paid_at <= et).all()
    for p in payments:
        a = Application.query.get(p.application_id)
        g = TourGroup.query.get(a.tour_group_id)
        rt = Route.query.get(g.route_id)
        ws.append([p.id, a.application_no, rt.route_name, g.group_code, a.responsible_name,
                   '订金' if p.payment_type == 'deposit' else '余款', p.amount,
                   p.paid_at.strftime('%Y-%m-%d %H:%M:%S')])
    buf = pyio.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f'财务导出_{ds}.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@finance_bp.route('/confirmations', methods=['GET'])
@jwt_required()
def get_confirmations():
    ds = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    td = datetime.strptime(ds, '%Y-%m-%d')
    st = datetime(td.year, td.month, td.day, 0, 0, 0)
    et = datetime(td.year, td.month, td.day, 23, 59, 59)
    apps = Application.query.filter(Application.status == 'completed',
                                     Application.completed_at >= st, Application.completed_at <= et).all()
    result = []
    for a in apps:
        g = TourGroup.query.get(a.tour_group_id)
        rt = Route.query.get(g.route_id)
        result.append({'application_no': a.application_no, 'route_name': rt.route_name,
                       'group_code': g.group_code, 'departure_date': g.departure_date.strftime('%Y-%m-%d'),
                       'responsible_name': a.responsible_name, 'responsible_phone': a.responsible_phone,
                       'adult_count': a.adult_count, 'child_count': a.child_count,
                       'total_amount': a.deposit_amount + a.balance_amount,
                       'deposit_paid': a.deposit_paid, 'balance_paid': a.balance_paid,
                       'balance_due_date': a.balance_due_date.strftime('%Y-%m-%d') if a.balance_due_date else None,
                       'print_balance_notice': not a.balance_paid})
    return ok(result)


@finance_bp.route('/confirmations/<app_no>/pdf', methods=['GET'])
@jwt_required()
def confirmation_pdf(app_no):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    import os as _os
    
    font_paths = [
        r'C:\Windows\Fonts\msyh.ttc',
        r'C:\Windows\Fonts\simsun.ttc',
        r'C:\Windows\Fonts\STSONG.TTF',
    ]
    chinese_font = 'Helvetica'
    for fp in font_paths:
        if _os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont('CNFont', fp))
                chinese_font = 'CNFont'
                break
            except:
                pass
    
    a = Application.query.filter_by(application_no=app_no).first()
    if not a: return not_found('申请不存在')
    g = TourGroup.query.get(a.tour_group_id)
    rt = Route.query.get(g.route_id)
    buf = pyio.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFont(f'{chinese_font}', 20)
    c.drawString(50, h - 50, '旅 游 确 认 书')
    c.setFont(f'{chinese_font}', 11)
    y = h - 90
    items = [
        f'确认编号: {a.application_no}',
        f'路线名称: {rt.route_name}',
        f'旅游团: {g.group_code}',
        f'出发日期: {g.departure_date}',
        f'责任人: {a.responsible_name}',
        f'联系电话: {a.responsible_phone}',
        f'人数: 成人 {a.adult_count} / 儿童 {a.child_count}',
        f'总费用: ¥{a.deposit_amount + a.balance_amount}',
        f'订金: ¥{a.deposit_amount}',
        f'余款: ¥{a.balance_amount}',
        f'状态: {"已完成" if a.status == "completed" else a.status}',
        f'确认日期: {datetime.now().strftime("%Y-%m-%d")}'
    ]
    for item in items:
        c.drawString(50, y, item)
        y -= 25
    c.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f'确认书_{app_no}.pdf', mimetype='application/pdf')
