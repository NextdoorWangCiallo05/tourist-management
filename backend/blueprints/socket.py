from flask_socketio import SocketIO, emit, join_room
from flask import request
from flask_jwt_extended import decode_token

socketio = SocketIO(cors_allowed_origins='*')
connected_users = {}


def init_socketio(app):
    socketio.init_app(app)


@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if token:
        try:
            data = decode_token(token)
            username = data.get('sub', 'anonymous')
            connected_users[request.sid] = username
            join_room(username)
            emit('notification', {'message': f'已连接到通知服务', 'type': 'success'})
        except:
            pass


@socketio.on('disconnect')
def handle_disconnect():
    connected_users.pop(request.sid, None)


def notify(username, message, type='info'):
    socketio.emit('notification', {'message': message, 'type': type}, room=username)
