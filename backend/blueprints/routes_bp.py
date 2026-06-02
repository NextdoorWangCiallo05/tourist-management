from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime
from models import db, Route, RouteHistory
from .response import ok, created, not_found

routes_bp = Blueprint('routes', __name__, url_prefix='/api/routes')


@routes_bp.route('', methods=['GET'])
@jwt_required()
def get_routes():
    routes = Route.query.all()
    return ok([{'id': r.id, 'route_code': r.route_code, 'route_name': r.route_name,
                'description': r.description, 'is_active': r.is_active, 'version': r.version} for r in routes])


@routes_bp.route('', methods=['POST'])
@jwt_required()
def create_route():
    data = request.get_json()
    r = Route(route_code=data['route_code'], route_name=data['route_name'], description=data.get('description', ''))
    db.session.add(r)
    db.session.commit()
    return created({'route_id': r.id}, '路线创建成功')


@routes_bp.route('/<int:route_id>', methods=['PUT'])
@jwt_required()
def update_route(route_id):
    r = Route.query.get(route_id)
    if not r: return not_found('路线不存在')
    data = request.get_json()
    history = RouteHistory(route_id=r.id, version=r.version, route_code=r.route_code, route_name=r.route_name, description=r.description, change_type='update')
    db.session.add(history)
    if 'route_name' in data: r.route_name = data['route_name']
    if 'description' in data: r.description = data['description']
    r.version += 1
    db.session.commit()
    return ok(None, '路线更新成功')


@routes_bp.route('/<int:route_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_route(route_id):
    r = Route.query.get(route_id)
    if not r: return not_found('路线不存在')
    history = RouteHistory(route_id=r.id, version=r.version, route_code=r.route_code, route_name=r.route_name, description=r.description, change_type='deactivate')
    db.session.add(history)
    r.is_active = False; r.version += 1
    db.session.commit()
    return ok(None, '路线已停用')


@routes_bp.route('/<int:route_id>/activate', methods=['POST'])
@jwt_required()
def activate_route(route_id):
    r = Route.query.get(route_id)
    if not r: return not_found('路线不存在')
    r.is_active = True
    db.session.commit()
    return ok(None, '路线已启用')
