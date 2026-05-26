from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
from models import db, Route, TourGroup, Application, Participant, PaymentRecord, PriceHistory, RouteHistory, User, AuditLog
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import csv
import io

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
jwt = JWTManager(app)
CORS(app)

def generate_application_no():
    chars = string.ascii_uppercase + string.digits
    return 'AP' + ''.join(random.choices(chars, k=8))

def generate_group_code():
    chars = string.ascii_uppercase + string.digits
    return 'TG' + ''.join(random.choices(chars, k=6))

def calculate_deposit_rate(days_before_departure):
    if days_before_departure >= 60:
        return 0.10
    elif days_before_departure >= 30:
        return 0.20
    else:
        return 1.00

def calculate_cancellation_fee(days_before_departure, total_amount):
    if days_before_departure >= 30:
        return 0
    elif days_before_departure >= 10:
        return total_amount * 0.20
    elif days_before_departure >= 1:
        return total_amount * 0.50
    else:
        return total_amount

def log_audit(action, target_type=None, target_id=None, detail=None):
    from flask_jwt_extended import get_jwt_identity
    try:
        username = get_jwt_identity()
    except:
        username = 'system'
    log = AuditLog(username=username, action=action, target_type=target_type, target_id=target_id, detail=detail)
    db.session.add(log)
    db.session.commit()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=username)
        log_audit('登录系统', 'user', username, f'用户 {username} 登录成功')
        return jsonify(
            access_token=access_token,
            display_name=user.display_name,
            role=user.role
        ), 200
    log_audit('登录失败', 'user', username, f'用户 {username} 登录失败')
    return jsonify({"msg": "Invalid username or password"}), 401

@app.route('/api/tour_groups', methods=['GET'])
@jwt_required()
def get_tour_groups():
    groups = TourGroup.query.filter_by(is_public=True).all()
    today = datetime.now().date()
    result = []
    for group in groups:
        route = Route.query.get(group.route_id)
        total_participants = 0
        applications = Application.query.filter(
            Application.tour_group_id == group.id,
            Application.status.in_(['pending', 'completed'])
        ).all()
        for app in applications:
            total_participants += app.adult_count + app.child_count
        remaining_capacity = max(0, group.max_capacity - total_participants)
        days_before_departure = (group.departure_date - today).days
        deposit_rate = calculate_deposit_rate(days_before_departure)
        result.append({
            'id': group.id,
            'group_code': group.group_code,
            'route_code': route.route_code,
            'route_name': route.route_name,
            'departure_date': group.departure_date.strftime('%Y-%m-%d'),
            'deadline_date': group.deadline_date.strftime('%Y-%m-%d'),
            'max_capacity': group.max_capacity,
            'remaining_capacity': remaining_capacity,
            'adult_price': group.adult_price,
            'child_price': group.child_price,
            'discount_rate': group.discount_rate,
            'deposit_rate': deposit_rate
        })
    return jsonify(result), 200

@app.route('/api/tour_groups/<int:group_id>/check_availability', methods=['GET'])
@jwt_required()
def check_availability(group_id):
    group = TourGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "Tour group not found"}), 404
    
    today = datetime.now().date()
    if today > group.deadline_date:
        return jsonify({"available": False, "reason": "已过截止日期"}), 200
    
    total_participants = 0
    applications = Application.query.filter(
        Application.tour_group_id == group_id,
        Application.status.in_(['pending', 'completed'])
    ).all()
    for app in applications:
        total_participants += app.adult_count + app.child_count
    
    if total_participants >= group.max_capacity:
        return jsonify({"available": False, "reason": "人数已满"}), 200
    
    return jsonify({"available": True, "reason": "可以办理申请"}), 200

@app.route('/api/applications', methods=['POST'])
@jwt_required()
def create_application():
    data = request.get_json()
    group_id = data['group_id']
    responsible_name = data['responsible_name']
    responsible_phone = data['phone_number']
    adult_count = data['adult_count']
    child_count = data['child_count']
    
    group = TourGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "Tour group not found"}), 404
    
    today = datetime.now().date()
    days_before_departure = (group.departure_date - today).days
    
    deposit_rate = calculate_deposit_rate(days_before_departure)
    total_price = adult_count * group.adult_price + child_count * group.child_price
    deposit_amount = round(total_price * deposit_rate, 2)
    
    application_no = generate_application_no()
    
    app = Application(
        application_no=application_no,
        tour_group_id=group_id,
        responsible_name=responsible_name,
        responsible_phone=responsible_phone,
        adult_count=adult_count,
        child_count=child_count,
        deposit_amount=deposit_amount,
        balance_amount=round(total_price - deposit_amount, 2),
        status='pending'
    )
    db.session.add(app)
    db.session.commit()
    
    log_audit('新建申请', 'application', application_no, f'申请编号 {application_no}，订金 {deposit_amount}')
    
    return jsonify({
        'application_no': application_no,
        'deposit_amount': deposit_amount,
        'total_price': total_price,
        'days_before_departure': days_before_departure,
        'deposit_rate': deposit_rate
    }), 201

@app.route('/api/applications/<string:app_no>/deposit', methods=['POST'])
@jwt_required()
def pay_deposit(app_no):
    data = request.get_json()
    amount_paid = data.get('amount_paid', 0)
    
    app = Application.query.filter_by(application_no=app_no).first()
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    if app.deposit_paid:
        return jsonify({"error": "Deposit already paid"}), 400
    
    if amount_paid >= app.deposit_amount:
        app.deposit_paid = True
        
        payment = PaymentRecord(
            application_id=app.id,
            payment_type='deposit',
            amount=amount_paid
        )
        db.session.add(payment)
        db.session.commit()
        
        log_audit('支付订金', 'application', app_no, f'申请 {app_no} 支付订金 {amount_paid}')
        
        return jsonify({"success": True, "message": "订金支付成功"}), 200
    else:
        return jsonify({"error": "支付金额不足"}), 400

@app.route('/api/applications/<string:app_no>/participants', methods=['POST'])
@jwt_required()
def add_participants(app_no):
    data = request.get_json()
    participants = data['participants']
    
    app = Application.query.filter_by(application_no=app_no).first()
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    for p_data in participants:
        participant = Participant(
            application_id=app.id,
            name=p_data['name'],
            gender=p_data.get('gender'),
            birth_date=datetime.strptime(p_data['birth_date'], '%Y-%m-%d').date() if p_data.get('birth_date') else None,
            id_type=p_data.get('id_type', '身份证'),
            id_number=p_data.get('id_number'),
            is_adult=p_data.get('is_adult', True),
            phone_number=p_data.get('phone_number') or p_data.get('phone'),
            address=p_data.get('address'),
            email=p_data.get('email'),
            postal_code=p_data.get('postal_code'),
            emergency_contact_name=p_data.get('emergency_contact_name'),
            emergency_contact_relation=p_data.get('emergency_contact_relation'),
            emergency_contact_address=p_data.get('emergency_contact_address'),
            emergency_contact_phone=p_data.get('emergency_contact_phone'),
            is_responsible=p_data.get('is_responsible', False)
        )
        db.session.add(participant)
    
    db.session.commit()
    return jsonify({"success": True, "message": "参加者信息录入成功"}), 200

@app.route('/api/applications/<string:app_no>/complete', methods=['POST'])
@jwt_required()
def complete_application(app_no):
    app = Application.query.filter_by(application_no=app_no).first()
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    if not app.deposit_paid:
        return jsonify({"error": "订金尚未支付"}), 400
    
    participant_count = Participant.query.filter_by(application_id=app.id).count()
    if participant_count < app.adult_count + app.child_count:
        return jsonify({"error": "参加者信息不完整"}), 400
    
    app.status = 'completed'
    app.completed_at = datetime.now()
    
    group = TourGroup.query.get(app.tour_group_id)
    today = datetime.now().date()
    days_before_departure = (group.departure_date - today).days
    
    if days_before_departure - 30 < 10:
        balance_due_date = today + timedelta(days=10)
    else:
        balance_due_date = group.departure_date - timedelta(days=30)
    
    app.balance_due_date = balance_due_date
    db.session.commit()
    
    log_audit('完成申请', 'application', app_no, f'申请 {app_no} 已完成')
    
    return jsonify({
        "success": True,
        "message": "申请完成",
        "balance_due_date": balance_due_date.strftime('%Y-%m-%d')
    }), 200

@app.route('/api/applications/<string:app_no>/balance', methods=['POST'])
@jwt_required()
def pay_balance(app_no):
    data = request.get_json()
    amount_paid = data.get('amount_paid', 0)
    
    app = Application.query.filter_by(application_no=app_no).first()
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    if app.balance_paid:
        return jsonify({"error": "余款已支付"}), 400
    
    if amount_paid >= app.balance_amount:
        app.balance_paid = True
        
        payment = PaymentRecord(
            application_id=app.id,
            payment_type='balance',
            amount=amount_paid
        )
        db.session.add(payment)
        db.session.commit()
        
        log_audit('支付余款', 'application', app_no, f'申请 {app_no} 支付余款 {amount_paid}')
        
        return jsonify({"success": True, "message": "余款支付成功"}), 200
    else:
        return jsonify({"error": "支付金额不足"}), 400

@app.route('/api/applications/<string:app_no>/cancel', methods=['POST'])
@jwt_required()
def cancel_application(app_no):
    app = Application.query.filter_by(application_no=app_no).first()
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    if app.status == 'cancelled':
        return jsonify({"error": "申请已取消"}), 400
    
    group = TourGroup.query.get(app.tour_group_id)
    today = datetime.now().date()
    days_before_departure = (group.departure_date - today).days
    
    total_paid = 0
    if app.deposit_paid:
        total_paid += app.deposit_amount
    if app.balance_paid:
        total_paid += app.balance_amount
    
    cancellation_fee = round(calculate_cancellation_fee(days_before_departure, total_paid), 2)
    refund_amount = round(total_paid - cancellation_fee, 2)
    
    app.status = 'cancelled'
    app.cancelled_at = datetime.now()
    db.session.commit()
    
    log_audit('取消申请', 'application', app_no, f'申请 {app_no} 已取消，退款 {refund_amount}')
    
    return jsonify({
        "success": True,
        "cancellation_fee": cancellation_fee,
        "refund_amount": refund_amount,
        "days_before_departure": days_before_departure
    }), 200

@app.route('/api/applications/<string:app_no>', methods=['GET'])
@jwt_required()
def get_application(app_no):
    app = Application.query.filter_by(application_no=app_no).first()
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    group = TourGroup.query.get(app.tour_group_id)
    route = Route.query.get(group.route_id)
    
    participants = Participant.query.filter_by(application_id=app.id).all()
    participant_list = []
    for p in participants:
        participant_list.append({
            'id': p.id,
            'name': p.name,
            'gender': p.gender,
            'birth_date': p.birth_date.strftime('%Y-%m-%d') if p.birth_date else None,
            'id_type': p.id_type,
            'id_number': p.id_number,
            'is_adult': p.is_adult,
            'phone': p.phone_number,
            'phone_number': p.phone_number,
            'address': p.address,
            'email': p.email,
            'is_responsible': p.is_responsible,
            'status': p.status
        })
    
    total_amount = app.adult_count * group.adult_price + app.child_count * group.child_price
    deposit_due_date = group.deadline_date.strftime('%Y-%m-%d') if group.deadline_date else None
    
    return jsonify({
        'id': app.id,
        'application_no': app.application_no,
        'tour_group_code': group.group_code,
        'route_name': route.route_name,
        'departure_date': group.departure_date.strftime('%Y-%m-%d'),
        'responsible_name': app.responsible_name,
        'responsible_phone': app.responsible_phone,
        'adult_count': app.adult_count,
        'child_count': app.child_count,
        'adult_price': group.adult_price,
        'child_price': group.child_price,
        'total_amount': total_amount,
        'deposit_amount': app.deposit_amount,
        'deposit_paid': app.deposit_paid,
        'deposit_due_date': deposit_due_date,
        'balance_amount': app.balance_amount,
        'balance_paid': app.balance_paid,
        'balance_due_date': app.balance_due_date.strftime('%Y-%m-%d') if app.balance_due_date else None,
        'status': app.status,
        'created_at': app.created_at.strftime('%Y-%m-%d %H:%M') if app.created_at else None,
        'participants': participant_list
    }), 200

@app.route('/api/applications', methods=['GET'])
@jwt_required()
def search_applications():
    args = request.args
    group_code = args.get('group_code')
    departure_date = args.get('departure_date')
    responsible_name = args.get('responsible_name')
    payment_no = args.get('payment_no')
    
    query = Application.query
    
    if group_code:
        group = TourGroup.query.filter_by(group_code=group_code).first()
        if group:
            query = query.filter_by(tour_group_id=group.id)
    
    if departure_date:
        group = TourGroup.query.filter(
            TourGroup.departure_date == datetime.strptime(departure_date, '%Y-%m-%d').date()
        ).first()
        if group:
            query = query.filter_by(tour_group_id=group.id)
    
    if responsible_name:
        query = query.filter(Application.responsible_name.like(f'%{responsible_name}%'))
    
    if payment_no:
        query = query.filter_by(application_no=payment_no)
    
    applications = query.all()
    result = []
    for app in applications:
        group = TourGroup.query.get(app.tour_group_id)
        route = Route.query.get(group.route_id)
        result.append({
            'id': app.id,
            'application_no': app.application_no,
            'group_code': group.group_code,
            'route_name': route.route_name,
            'departure_date': group.departure_date.strftime('%Y-%m-%d'),
            'responsible_name': app.responsible_name,
            'status': app.status,
            'created_at': app.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify(result), 200

@app.route('/api/routes', methods=['POST'])
@jwt_required()
def create_route():
    data = request.get_json()
    route_code = data['route_code']
    route_name = data['route_name']
    description = data.get('description', '')
    
    if Route.query.filter_by(route_code=route_code).first():
        return jsonify({"error": "路线代码已存在"}), 400
    
    route = Route(
        route_code=route_code,
        route_name=route_name,
        description=description
    )
    db.session.add(route)
    db.session.commit()
    
    return jsonify({"success": True, "route_id": route.id}), 201

@app.route('/api/routes', methods=['GET'])
@jwt_required()
def get_routes():
    routes = Route.query.all()
    result = []
    for route in routes:
        result.append({
            'id': route.id,
            'route_code': route.route_code,
            'route_name': route.route_name,
            'description': route.description,
            'is_active': route.is_active,
            'version': route.version
        })
    return jsonify(result), 200

@app.route('/api/routes/<int:route_id>', methods=['PUT'])
@jwt_required()
def update_route(route_id):
    data = request.get_json()
    route = Route.query.get(route_id)
    if not route:
        return jsonify({"error": "Route not found"}), 404
    
    history = RouteHistory(
        route_id=route.id,
        version=route.version,
        route_code=route.route_code,
        route_name=route.route_name,
        description=route.description,
        change_type='update'
    )
    db.session.add(history)
    
    if 'route_name' in data:
        route.route_name = data['route_name']
    if 'description' in data:
        route.description = data['description']
    
    route.version += 1
    db.session.commit()
    
    return jsonify({"success": True, "message": "路线更新成功"}), 200

@app.route('/api/routes/<int:route_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_route(route_id):
    route = Route.query.get(route_id)
    if not route:
        return jsonify({"error": "Route not found"}), 404
    
    history = RouteHistory(
        route_id=route.id,
        version=route.version,
        route_code=route.route_code,
        route_name=route.route_name,
        description=route.description,
        change_type='deactivate'
    )
    db.session.add(history)
    
    route.is_active = False
    route.version += 1
    db.session.commit()
    
    return jsonify({"success": True, "message": "路线已停用"}), 200

@app.route('/api/tour_groups', methods=['POST'])
@jwt_required()
def create_tour_group():
    data = request.get_json()
    route_id = data['route_id']
    departure_date = datetime.strptime(data['departure_date'], '%Y-%m-%d').date()
    deadline_date = datetime.strptime(data['deadline_date'], '%Y-%m-%d').date()
    max_capacity = data['max_capacity']
    adult_price = data['adult_price']
    child_price = data['child_price']
    discount_rate = data.get('discount_rate', 0.0)
    
    if not Route.query.get(route_id):
        return jsonify({"error": "Route not found"}), 404
    
    group_code = generate_group_code()
    
    group = TourGroup(
        group_code=group_code,
        route_id=route_id,
        departure_date=departure_date,
        deadline_date=deadline_date,
        max_capacity=max_capacity,
        adult_price=adult_price,
        child_price=child_price,
        discount_rate=discount_rate,
        is_public=False
    )
    db.session.add(group)
    db.session.commit()
    
    return jsonify({"success": True, "group_code": group_code}), 201

@app.route('/api/tour_groups/<int:group_id>/price', methods=['PUT'])
@jwt_required()
def update_tour_group_price(group_id):
    data = request.get_json()
    group = TourGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "Tour group not found"}), 404
    
    if group.is_public:
        return jsonify({"error": "已公开的旅游团价格不能修改"}), 400
    
    price_history = PriceHistory(
        tour_group_id=group.id,
        adult_price=group.adult_price,
        child_price=group.child_price,
        discount_rate=group.discount_rate
    )
    db.session.add(price_history)
    
    if 'adult_price' in data:
        group.adult_price = data['adult_price']
    if 'child_price' in data:
        group.child_price = data['child_price']
    if 'discount_rate' in data:
        group.discount_rate = data['discount_rate']
    
    db.session.commit()
    
    return jsonify({"success": True, "message": "价格更新成功"}), 201

@app.route('/api/tour_groups/<int:group_id>/publish', methods=['POST'])
@jwt_required()
def publish_tour_group(group_id):
    group = TourGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "Tour group not found"}), 404
    
    if group.is_public:
        return jsonify({"error": "旅游团已公开"}), 400
    
    group.is_public = True
    db.session.commit()
    
    return jsonify({"success": True, "message": "旅游团已公开"}), 200

@app.route('/api/tour_groups/all', methods=['GET'])
@jwt_required()
def get_all_tour_groups():
    groups = TourGroup.query.all()
    result = []
    for group in groups:
        route = Route.query.get(group.route_id)
        result.append({
            'id': group.id,
            'group_code': group.group_code,
            'route_id': group.route_id,
            'route_code': route.route_code,
            'route_name': route.route_name,
            'departure_date': group.departure_date.strftime('%Y-%m-%d'),
            'deadline_date': group.deadline_date.strftime('%Y-%m-%d'),
            'max_capacity': group.max_capacity,
            'adult_price': group.adult_price,
            'child_price': group.child_price,
            'discount_rate': group.discount_rate,
            'is_public': group.is_public
        })
    return jsonify(result), 200

@app.route('/api/tour_groups/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_tour_group(group_id):
    data = request.get_json()
    group = TourGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "Tour group not found"}), 404
    
    if 'route_id' in data:
        group.route_id = data['route_id']
    if 'departure_date' in data:
        group.departure_date = datetime.strptime(data['departure_date'], '%Y-%m-%d').date()
    if 'deadline_date' in data:
        group.deadline_date = datetime.strptime(data['deadline_date'], '%Y-%m-%d').date()
    if 'max_capacity' in data:
        group.max_capacity = data['max_capacity']
    if 'adult_price' in data:
        group.adult_price = data['adult_price']
    if 'child_price' in data:
        group.child_price = data['child_price']
    if 'discount_rate' in data:
        group.discount_rate = data['discount_rate']
    
    db.session.commit()
    return jsonify({"success": True, "message": "旅游团更新成功"}), 200

@app.route('/api/tour_groups/<int:group_id>/unpublish', methods=['POST'])
@jwt_required()
def unpublish_tour_group(group_id):
    group = TourGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "Tour group not found"}), 404
    
    if not group.is_public:
        return jsonify({"error": "旅游团未公开"}), 400
    
    group.is_public = False
    db.session.commit()
    
    return jsonify({"success": True, "message": "旅游团已取消公开"}), 200

@app.route('/api/participants/<int:participant_id>', methods=['PUT'])
@jwt_required()
def update_participant(participant_id):
    data = request.get_json()
    participant = Participant.query.get(participant_id)
    if not participant:
        return jsonify({"error": "Participant not found"}), 404
    
    if 'name' in data:
        participant.name = data['name']
    if 'gender' in data:
        participant.gender = data['gender']
    if 'phone_number' in data:
        participant.phone_number = data['phone_number']
    if 'address' in data:
        participant.address = data['address']
    if 'email' in data:
        participant.email = data['email']
    
    db.session.commit()
    return jsonify({"success": True, "message": "参加者信息更新成功"}), 200

@app.route('/api/participants/<int:participant_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_participant(participant_id):
    data = request.get_json()
    participant = Participant.query.get(participant_id)
    if not participant:
        return jsonify({"error": "Participant not found"}), 404
    
    if participant.is_responsible:
        if not data.get('new_responsible_id'):
            return jsonify({"error": "取消申请责任人时必须指定新的责任人"}), 400
        
        new_responsible = Participant.query.get(data['new_responsible_id'])
        if not new_responsible:
            return jsonify({"error": "新责任人不存在"}), 404
        
        new_responsible.is_responsible = True
    
    participant.status = 'cancelled'
    db.session.commit()
    
    return jsonify({"success": True, "message": "参加者已取消"}), 200

@app.route('/api/daily_export', methods=['GET'])
@jwt_required()
def daily_export():
    date_str = request.args.get('date')
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = datetime.now().date()
    start_time = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    end_time = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    
    payments = PaymentRecord.query.filter(
        PaymentRecord.paid_at >= start_time,
        PaymentRecord.paid_at <= end_time
    ).all()
    
    export_data = []
    for payment in payments:
        app = Application.query.get(payment.application_id)
        group = TourGroup.query.get(app.tour_group_id)
        route = Route.query.get(group.route_id)
        
        export_data.append({
            'payment_id': payment.id,
            'application_no': app.application_no,
            'route_name': route.route_name,
            'group_code': group.group_code,
            'responsible_name': app.responsible_name,
            'payment_type': payment.payment_type,
            'amount': payment.amount,
            'paid_at': payment.paid_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(export_data), 200

@app.route('/api/confirmations', methods=['GET'])
@jwt_required()
def get_confirmations():
    date_str = request.args.get('date')
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = datetime.now().date()
    start_time = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    end_time = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    
    applications = Application.query.filter(
        Application.status == 'completed',
        Application.completed_at >= start_time,
        Application.completed_at <= end_time
    ).all()
    
    result = []
    for app in applications:
        group = TourGroup.query.get(app.tour_group_id)
        route = Route.query.get(group.route_id)
        
        result.append({
            'application_no': app.application_no,
            'route_name': route.route_name,
            'group_code': group.group_code,
            'departure_date': group.departure_date.strftime('%Y-%m-%d'),
            'responsible_name': app.responsible_name,
            'responsible_phone': app.responsible_phone,
            'adult_count': app.adult_count,
            'child_count': app.child_count,
            'total_amount': app.deposit_amount + app.balance_amount,
            'deposit_paid': app.deposit_paid,
            'balance_paid': app.balance_paid,
            'balance_due_date': app.balance_due_date.strftime('%Y-%m-%d') if app.balance_due_date else None,
            'print_balance_notice': not app.balance_paid
        })
    
    return jsonify(result), 200


@app.route('/api/stats', methods=['GET'])
@jwt_required()
def get_stats():
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    total_apps = Application.query.count()
    total_groups = TourGroup.query.count()
    total_routes = Route.query.count()
    total_participants = Participant.query.count()
    
    today_apps = Application.query.filter(db.func.date(Application.created_at) == today).count()
    
    status_distribution = db.session.query(
        Application.status, db.func.count(Application.id)
    ).group_by(Application.status).all()
    
    daily_trend = db.session.query(
        db.func.date(Application.created_at).label('date'),
        db.func.count(Application.id)
    ).filter(Application.created_at >= week_ago).group_by(
        db.func.date(Application.created_at)
    ).order_by(db.func.date(Application.created_at)).all()
    
    payment_total = db.session.query(db.func.sum(PaymentRecord.amount)).scalar() or 0
    
    return jsonify({
        'total_applications': total_apps,
        'total_groups': total_groups,
        'total_routes': total_routes,
        'total_participants': total_participants,
        'today_applications': today_apps,
        'today_payments': payment_total,
        'status_distribution': [{'name': s, 'value': c} for s, c in status_distribution],
        'daily_trend': [{'date': str(d), 'count': c} for d, c in daily_trend]
    }), 200


@app.route('/api/routes/<int:route_id>/activate', methods=['POST'])
@jwt_required()
def activate_route(route_id):
    route = Route.query.get(route_id)
    if not route:
        return jsonify({"error": "Route not found"}), 404
    
    route.is_active = True
    db.session.commit()
    
    log_audit('启用路线', 'route', str(route_id), f'路线 {route.route_name} 已启用')
    
    return jsonify({"success": True, "message": "路线已启用"}), 200


@app.route('/api/applications/<string:app_no>/participants/import', methods=['POST'])
@jwt_required()
def import_participants(app_no):
    app = Application.query.filter_by(application_no=app_no).first()
    if not app:
        return jsonify({"error": "Application not found"}), 404
    
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "请上传文件"}), 400
    
    content = file.read().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(content))
    
    count = 0
    for row in reader:
        participant = Participant(
            application_id=app.id,
            name=row.get('姓名', ''),
            id_type=row.get('证件类型', '身份证'),
            id_number=row.get('证件号码', ''),
            is_adult=row.get('类型', '成人') == '成人',
            phone_number=row.get('联系电话', ''),
            gender=row.get('性别', ''),
            address=row.get('地址', '')
        )
        db.session.add(participant)
        count += 1
    
    db.session.commit()
    log_audit('批量导入', 'application', app_no, f'申请 {app_no} 批量导入 {count} 名参加者')
    
    return jsonify({"success": True, "count": count, "message": f"成功导入 {count} 名参加者"}), 201


@app.route('/api/audit_logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    action = request.args.get('action')
    
    query = AuditLog.query.order_by(AuditLog.created_at.desc())
    if action:
        query = query.filter(AuditLog.action.like(f'%{action}%'))
    
    logs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'logs': [{
            'id': l.id,
            'username': l.username,
            'action': l.action,
            'target_type': l.target_type,
            'target_id': l.target_id,
            'detail': l.detail,
            'created_at': l.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for l in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'page': page
    }), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                display_name='王经理',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=5000)