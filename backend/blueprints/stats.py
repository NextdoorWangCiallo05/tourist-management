from flask import Blueprint
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from models import db, Application, TourGroup, Route, Participant, PaymentRecord, AuditLog
from .response import ok

stats_bp = Blueprint('stats', __name__, url_prefix='/api')


@stats_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    sd = db.session.query(Application.status, db.func.count(Application.id)).group_by(Application.status).all()
    dt = db.session.query(db.func.date(Application.created_at).label('d'), db.func.count(Application.id))\
        .filter(Application.created_at >= week_ago).group_by(db.func.date(Application.created_at))\
        .order_by(db.func.date(Application.created_at)).all()
    return ok({
        'total_applications': Application.query.count(),
        'total_groups': TourGroup.query.count(),
        'total_routes': Route.query.count(),
        'total_participants': Participant.query.count(),
        'today_applications': Application.query.filter(db.func.date(Application.created_at) == today).count(),
        'today_payments': db.session.query(db.func.sum(PaymentRecord.amount)).scalar() or 0,
        'status_distribution': [{'name': s, 'value': c} for s, c in sd],
        'daily_trend': [{'date': str(d), 'count': c} for d, c in dt]
    })
