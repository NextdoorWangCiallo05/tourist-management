from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, AuditLog
from .response import ok, fail, not_found

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


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    display_name = data.get('display_name', '').strip() or username
    if not username or not password:
        return fail('用户名和密码不能为空')
    if len(password) < 6:
        return fail('密码长度不少于6位')
    if User.query.filter_by(username=username).first():
        return fail('用户名已存在')
    user = User(username=username, password_hash=generate_password_hash(password),
                display_name=display_name, role='operator')
    db.session.add(user)
    db.session.commit()
    log = AuditLog(username=username, action='注册账户', target_type='user', target_id=username, detail=f'新用户注册 {username}')
    db.session.add(log)
    db.session.commit()
    return ok({'username': username, 'display_name': display_name, 'role': 'operator'}, '注册成功')


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    current = get_jwt_identity()
    user = User.query.filter_by(username=current).first()
    if not user or user.role != 'admin':
        return fail('仅管理员可查看用户列表', 403)
    users = User.query.all()
    return ok([{
        'id': u.id, 'username': u.username, 'display_name': u.display_name,
        'role': u.role, 'created_at': u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else ''
    } for u in users])


@auth_bp.route('/users/<int:uid>/role', methods=['PUT'])
@jwt_required()
def update_role(uid):
    current = get_jwt_identity()
    admin = User.query.filter_by(username=current).first()
    if not admin or admin.role != 'admin':
        return fail('仅管理员可修改角色', 403)
    target = User.query.get(uid)
    if not target:
        return not_found('用户不存在')
    data = request.get_json()
    new_role = data.get('role')
    if new_role not in ('admin', 'operator'):
        return fail('角色无效')
    target.role = new_role
    db.session.commit()
    log = AuditLog(username=current, action='修改用户角色', target_type='user', target_id=target.username, detail=f'设置角色为 {new_role}')
    db.session.add(log)
    db.session.commit()
    return ok(None, '角色更新成功')


@auth_bp.route('/users/<int:uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    current = get_jwt_identity()
    admin = User.query.filter_by(username=current).first()
    if not admin or admin.role != 'admin':
        return fail('仅管理员可删除用户', 403)
    target = User.query.get(uid)
    if not target:
        return not_found('用户不存在')
    if target.username == current:
        return fail('不能删除自己')
    if target.role == 'admin':
        return fail('不能删除其他管理员')
    db.session.delete(target)
    db.session.commit()
    log = AuditLog(username=current, action='删除用户', target_type='user', target_id=target.username, detail=f'删除用户 {target.username}')
    db.session.add(log)
    db.session.commit()
    return ok(None, '用户已删除')
