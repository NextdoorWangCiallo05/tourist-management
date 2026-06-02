from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from models import db, User, AuditLog
from .response import ok, fail

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        token = create_access_token(identity=username)
        log = AuditLog(username=username, action='登录系统', target_type='user', target_id=username, detail=f'用户 {username} 登录成功')
        db.session.add(log)
        db.session.commit()
        return ok({'access_token': token, 'display_name': user.display_name, 'role': user.role})
    log = AuditLog(username=username, action='登录失败', target_type='user', target_id=username, detail=f'用户 {username} 登录失败')
    db.session.add(log)
    db.session.commit()
    return fail('用户名或密码错误', 401)
