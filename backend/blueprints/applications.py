from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db, Application, Participant, PaymentRecord, TourGroup, Route, AuditLog
from .response import ok, created, fail, not_found
import random, string, csv, io

apps_bp = Blueprint('applications', __name__, url_prefix='/api/applications')


def gen_no():
    return 'AP' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def calc_deposit_rate(days):
    if days >= 60: return 0.10
    if days >= 30: return 0.20
    return 1.00


def calc_cancel_fee(days, total):
    if days >= 30: return 0
    if days >= 10: return total * 0.20
    if days >= 1: return total * 0.50
    return total


def log_audit(action, target_type=None, target_id=None, detail=None):
    user = get_jwt_identity()
    db.session.add(AuditLog(username=user, action=action, target_type=target_type, target_id=target_id, detail=detail))
    db.session.commit()


@apps_bp.route('', methods=['GET'])
@jwt_required()
def search():
    args = request.args
    q = Application.query
    gc = args.get('group_code')
    if gc:
        g = TourGroup.query.filter_by(group_code=gc).first()
        if g: q = q.filter_by(tour_group_id=g.id)
    rn = args.get('responsible_name')
    if rn: q = q.filter(Application.responsible_name.like(f'%{rn}%'))
    an = args.get('application_no')
    if an: q = q.filter_by(application_no=an)
    apps = q.all()
    result = []
    for a in apps:
        g = TourGroup.query.get(a.tour_group_id)
        rt = Route.query.get(g.route_id)
        result.append({'id': a.id, 'application_no': a.application_no, 'group_code': g.group_code,
                       'route_name': rt.route_name, 'departure_date': g.departure_date.strftime('%Y-%m-%d'),
                       'responsible_name': a.responsible_name, 'status': a.status,
                       'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')})
    return ok(result)


@apps_bp.route('', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    g = TourGroup.query.get(data['group_id'])
    if not g: return not_found('旅游团不存在')
    today = datetime.now().date()
    rate = calc_deposit_rate((g.departure_date - today).days)
    total = data['adult_count'] * g.adult_price + data['child_count'] * g.child_price
    deposit = round(total * rate, 2)
    no = gen_no()
    a = Application(application_no=no, tour_group_id=g.id, responsible_name=data['responsible_name'],
                    responsible_phone=data['phone_number'], adult_count=data['adult_count'],
                    child_count=data['child_count'], deposit_amount=deposit,
                    balance_amount=round(total - deposit, 2), status='pending')
    db.session.add(a)
    db.session.commit()
    log_audit('新建申请', 'application', no, f'申请编号 {no}，订金 {deposit}')
    return created({'application_no': no, 'deposit_amount': deposit, 'total_price': total}, '申请创建成功')


@apps_bp.route('/<app_no>', methods=['GET'])
@jwt_required()
def detail(app_no):
    a = Application.query.filter_by(application_no=app_no).first()
    if not a: return not_found('申请不存在')
    g = TourGroup.query.get(a.tour_group_id)
    rt = Route.query.get(g.route_id)
    participants = Participant.query.filter_by(application_id=a.id).all()
    total = a.adult_count * g.adult_price + a.child_count * g.child_price
    return ok({
        'id': a.id, 'application_no': a.application_no, 'tour_group_code': g.group_code,
        'route_name': rt.route_name, 'departure_date': g.departure_date.strftime('%Y-%m-%d'),
        'responsible_name': a.responsible_name, 'responsible_phone': a.responsible_phone,
        'adult_count': a.adult_count, 'child_count': a.child_count,
        'adult_price': g.adult_price, 'child_price': g.child_price,
        'total_amount': total, 'deposit_amount': a.deposit_amount, 'deposit_paid': a.deposit_paid,
        'deposit_due_date': g.deadline_date.strftime('%Y-%m-%d') if g.deadline_date else None,
        'balance_amount': a.balance_amount, 'balance_paid': a.balance_paid,
        'balance_due_date': a.balance_due_date.strftime('%Y-%m-%d') if a.balance_due_date else None,
        'status': a.status, 'created_at': a.created_at.strftime('%Y-%m-%d %H:%M') if a.created_at else None,
        'participants': [{
            'id': p.id, 'name': p.name, 'gender': p.gender,
            'birth_date': p.birth_date.strftime('%Y-%m-%d') if p.birth_date else None,
            'id_type': p.id_type, 'id_number': p.id_number, 'is_adult': p.is_adult,
            'phone': p.phone_number, 'phone_number': p.phone_number,
            'address': p.address, 'email': p.email, 'is_responsible': p.is_responsible, 'status': p.status
        } for p in participants]
    })


@apps_bp.route('/<app_no>/participants', methods=['POST'])
@jwt_required()
def add_participants(app_no):
    a = Application.query.filter_by(application_no=app_no).first()
    if not a: return not_found('申请不存在')
    data = request.get_json()
    items = data if isinstance(data, list) else data.get('participants', [data])
    for p in items:
        db.session.add(Participant(
            application_id=a.id, name=p['name'], id_type=p.get('id_type', '身份证'),
            id_number=p.get('id_number', ''), is_adult=p.get('is_adult', True),
            phone_number=p.get('phone_number') or p.get('phone', ''),
            gender=p.get('gender'), address=p.get('address', ''),
            is_responsible=p.get('is_responsible', False)
        ))
    db.session.commit()
    return ok(None, '参加者添加成功')


@apps_bp.route('/<app_no>/participants/import', methods=['POST'])
@jwt_required()
def import_participants(app_no):
    a = Application.query.filter_by(application_no=app_no).first()
    if not a: return not_found('申请不存在')
    file = request.files.get('file')
    if not file: return fail('请上传文件')
    reader = csv.DictReader(io.StringIO(file.read().decode('utf-8-sig')))
    count = 0
    for row in reader:
        db.session.add(Participant(application_id=a.id, name=row.get('姓名', ''),
            id_type=row.get('证件类型', '身份证'), id_number=row.get('证件号码', ''),
            is_adult=row.get('类型', '成人') == '成人', phone_number=row.get('联系电话', ''),
            gender=row.get('性别', ''), address=row.get('地址', '')))
        count += 1
    db.session.commit()
    log_audit('批量导入', 'application', app_no, f'导入 {count} 名参加者')
    return created({'count': count}, f'成功导入 {count} 名参加者')


@apps_bp.route('/<app_no>/deposit', methods=['POST'])
@jwt_required()
def pay_deposit(app_no):
    a = Application.query.filter_by(application_no=app_no).first()
    if not a: return not_found('申请不存在')
    if a.deposit_paid: return fail('订金已支付')
    amt = request.get_json().get('amount_paid', 0)
    if amt < a.deposit_amount: return fail('支付金额不足')
    a.deposit_paid = True
    db.session.add(PaymentRecord(application_id=a.id, payment_type='deposit', amount=amt))
    log_audit('支付订金', 'application', app_no, f'支付订金 {amt}')
    db.session.commit()
    return ok(None, '订金支付成功')


@apps_bp.route('/<app_no>/balance', methods=['POST'])
@jwt_required()
def pay_balance(app_no):
    a = Application.query.filter_by(application_no=app_no).first()
    if not a: return not_found('申请不存在')
    if a.balance_paid: return fail('余款已支付')
    amt = request.get_json().get('amount_paid', 0)
    if amt < a.balance_amount: return fail('支付金额不足')
    a.balance_paid = True
    db.session.add(PaymentRecord(application_id=a.id, payment_type='balance', amount=amt))
    log_audit('支付余款', 'application', app_no, f'支付余款 {amt}')
    db.session.commit()
    return ok(None, '余款支付成功')


@apps_bp.route('/<app_no>/complete', methods=['POST'])
@jwt_required()
def complete(app_no):
    a = Application.query.filter_by(application_no=app_no).first()
    if not a: return not_found('申请不存在')
    if not a.deposit_paid: return fail('订金尚未支付')
    cnt = Participant.query.filter_by(application_id=a.id).count()
    if cnt < a.adult_count + a.child_count: return fail('参加者信息不完整')
    a.status = 'completed'
    a.completed_at = datetime.now()
    g = TourGroup.query.get(a.tour_group_id)
    days = (g.departure_date - datetime.now().date()).days
    a.balance_due_date = (datetime.now().date() + timedelta(days=10)) if days - 30 < 10 else (g.departure_date - timedelta(days=30))
    log_audit('完成申请', 'application', app_no, f'申请 {app_no} 已完成')
    db.session.commit()
    return ok({'balance_due_date': a.balance_due_date.strftime('%Y-%m-%d')}, '申请完成')


@apps_bp.route('/<app_no>/cancel', methods=['POST'])
@jwt_required()
def cancel(app_no):
    a = Application.query.filter_by(application_no=app_no).first()
    if not a: return not_found('申请不存在')
    if a.status == 'cancelled': return fail('申请已取消')
    g = TourGroup.query.get(a.tour_group_id)
    days = (g.departure_date - datetime.now().date()).days
    total_paid = (a.deposit_amount if a.deposit_paid else 0) + (a.balance_amount if a.balance_paid else 0)
    fee = round(calc_cancel_fee(days, total_paid), 2)
    refund = round(total_paid - fee, 2)
    a.status = 'cancelled'
    a.cancelled_at = datetime.now()
    log_audit('取消申请', 'application', app_no, f'取消，退款 {refund}')
    db.session.commit()
    return ok({'cancellation_fee': fee, 'refund_amount': refund}, '申请已取消')
