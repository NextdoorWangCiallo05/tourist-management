from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime
from models import db, Route, TourGroup, PriceHistory
from .response import ok, created, fail, not_found

groups_bp = Blueprint('groups', __name__, url_prefix='/api/tour_groups')


def calc_deposit_rate(days):
    if days >= 60: return 0.10
    if days >= 30: return 0.20
    return 1.00


@groups_bp.route('', methods=['GET'])
@jwt_required()
def get_groups():
    groups = TourGroup.query.filter_by(is_public=True).all()
    today = datetime.now().date()
    result = []
    for g in groups:
        route = Route.query.get(g.route_id)
        apps = [a for a in g.applications if a.status in ('pending', 'completed')]
        used = sum(a.adult_count + a.child_count for a in apps)
        result.append({
            'id': g.id, 'group_code': g.group_code,
            'route_code': route.route_code, 'route_name': route.route_name,
            'departure_date': g.departure_date.strftime('%Y-%m-%d'),
            'deadline_date': g.deadline_date.strftime('%Y-%m-%d'),
            'max_capacity': g.max_capacity,
            'remaining_capacity': max(0, g.max_capacity - used),
            'adult_price': g.adult_price, 'child_price': g.child_price,
            'discount_rate': g.discount_rate,
            'deposit_rate': calc_deposit_rate((g.departure_date - today).days)
        })
    return ok(result)


@groups_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_groups():
    groups = TourGroup.query.all()
    result = []
    for g in groups:
        route = Route.query.get(g.route_id)
        result.append({
            'id': g.id, 'group_code': g.group_code,
            'route_id': g.route_id, 'route_code': route.route_code,
            'route_name': route.route_name,
            'departure_date': g.departure_date.strftime('%Y-%m-%d'),
            'deadline_date': g.deadline_date.strftime('%Y-%m-%d'),
            'max_capacity': g.max_capacity, 'adult_price': g.adult_price,
            'child_price': g.child_price, 'is_public': g.is_public
        })
    return ok(result)


@groups_bp.route('', methods=['POST'])
@jwt_required()
def create_group():
    data = request.get_json()
    g = TourGroup(
        group_code=data['group_code'],
        route_id=data['route_id'],
        departure_date=datetime.strptime(data['departure_date'], '%Y-%m-%d').date(),
        deadline_date=datetime.strptime(data['deadline_date'], '%Y-%m-%d').date(),
        max_capacity=data['max_capacity'],
        adult_price=data['adult_price'],
        child_price=data['child_price']
    )
    db.session.add(g)
    db.session.commit()
    return created({'group_code': g.group_code}, '旅游团创建成功')


@groups_bp.route('/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    g = TourGroup.query.get(group_id)
    if not g: return not_found('旅游团不存在')
    data = request.get_json()
    for k in ('route_id', 'max_capacity', 'adult_price', 'child_price', 'discount_rate'):
        if k in data: setattr(g, k, data[k])
    for k in ('departure_date', 'deadline_date'):
        if k in data: setattr(g, k, datetime.strptime(data[k], '%Y-%m-%d').date())
    db.session.commit()
    return ok(None, '旅游团更新成功')


@groups_bp.route('/<int:group_id>/check_availability', methods=['GET'])
def check_availability(group_id):
    g = TourGroup.query.get(group_id)
    if not g: return not_found('旅游团不存在')
    today = datetime.now().date()
    if today > g.deadline_date:
        return ok({'available': False, 'reason': '已过截止日期'})
    used = sum(a.adult_count + a.child_count for a in g.applications if a.status in ('pending', 'completed'))
    if used >= g.max_capacity:
        return ok({'available': False, 'reason': '人数已满'})
    return ok({'available': True, 'reason': '可以办理申请'})


@groups_bp.route('/<int:group_id>/price', methods=['PUT'])
@jwt_required()
def update_price(group_id):
    g = TourGroup.query.get(group_id)
    if not g: return not_found('旅游团不存在')
    if g.is_public: return fail('已公开的旅游团价格不能修改')
    data = request.get_json()
    history = PriceHistory(tour_group_id=g.id, adult_price=g.adult_price, child_price=g.child_price, discount_rate=g.discount_rate)
    db.session.add(history)
    if 'adult_price' in data: g.adult_price = data['adult_price']
    if 'child_price' in data: g.child_price = data['child_price']
    if 'discount_rate' in data: g.discount_rate = data['discount_rate']
    db.session.commit()
    return ok(None, '价格更新成功')


@groups_bp.route('/<int:group_id>/publish', methods=['POST'])
@jwt_required()
def publish(group_id):
    g = TourGroup.query.get(group_id)
    if not g: return not_found('旅游团不存在')
    if g.is_public: return fail('旅游团已公开')
    g.is_public = True
    db.session.commit()
    return ok(None, '旅游团已公开')


@groups_bp.route('/<int:group_id>/unpublish', methods=['POST'])
@jwt_required()
def unpublish(group_id):
    g = TourGroup.query.get(group_id)
    if not g: return not_found('旅游团不存在')
    if not g.is_public: return fail('旅游团未公开')
    g.is_public = False
    db.session.commit()
    return ok(None, '旅游团已取消公开')
