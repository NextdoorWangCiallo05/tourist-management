from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models import db, Participant, Application
from .response import ok, not_found, fail

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
    a = Application.query.get(p.application_id)
    # 如果被取消者是责任人，需指定新责任人
    if p.is_responsible:
        data = request.get_json()
        new_responsible_id = data.get('new_responsible_id')
        if not new_responsible_id:
            remaining = Participant.query.filter(
                Participant.application_id == a.id,
                Participant.id != pid,
                Participant.status == 'active'
            ).count()
            if remaining > 0:
                return fail('该参加者是责任人，请指定新的责任人', 400)
        else:
            new_p = Participant.query.get(new_responsible_id)
            if new_p and new_p.application_id == a.id:
                new_p.is_responsible = True
                a.responsible_name = new_p.name
                a.responsible_phone = new_p.phone_number or a.responsible_phone
    p.status = 'cancelled'
    p.is_responsible = False
    db.session.commit()
    return ok(None, '参加者已取消')
