from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models import AuditLog
from .response import ok

logs_bp = Blueprint('logs', __name__, url_prefix='/api/audit_logs')


@logs_bp.route('', methods=['GET'])
@jwt_required()
def get_logs():
    page = request.args.get('page', 1, type=int)
    per = request.args.get('per_page', 50, type=int)
    action = request.args.get('action')
    q = AuditLog.query.order_by(AuditLog.created_at.desc())
    if action: q = q.filter(AuditLog.action.like(f'%{action}%'))
    logs = q.paginate(page=page, per_page=per, error_out=False)
    return ok({
        'logs': [{'id': l.id, 'username': l.username, 'action': l.action,
                   'target_type': l.target_type, 'target_id': l.target_id,
                   'detail': l.detail, 'created_at': l.created_at.strftime('%Y-%m-%d %H:%M:%S')} for l in logs.items],
        'total': logs.total, 'pages': logs.pages, 'page': page
    })
