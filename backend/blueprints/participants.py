from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models import db, Participant
from .response import ok, not_found

parts_bp = Blueprint('participants', __name__, url_prefix='/api/participants')


@parts_bp.route('/<int:pid>', methods=['PUT'])
@jwt_required()
def update(pid):
    p = Participant.query.get(pid)
    if not p: return not_found('参加者不存在')
    data = request.get_json()
    for k in ('name', 'gender', 'phone_number', 'address', 'email', 'id_type', 'id_number', 'is_adult'):
        if k in data: setattr(p, k, data[k])
    db.session.commit()
    return ok(None, '参加者信息更新成功')


@parts_bp.route('/<int:pid>/cancel', methods=['POST'])
@jwt_required()
def cancel(pid):
    p = Participant.query.get(pid)
    if not p: return not_found('参加者不存在')
    p.status = 'cancelled'
    db.session.commit()
    return ok(None, '参加者已取消')
