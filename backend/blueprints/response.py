from flask import jsonify


def ok(data=None, message='成功'):
    return jsonify({'code': 200, 'message': message, 'data': data}), 200


def created(data=None, message='创建成功'):
    return jsonify({'code': 201, 'message': message, 'data': data}), 201


def fail(message='请求失败', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def not_found(message='资源不存在'):
    return jsonify({'code': 404, 'message': message, 'data': None}), 404


def unauthorized(message='未授权'):
    return jsonify({'code': 401, 'message': message, 'data': None}), 401
