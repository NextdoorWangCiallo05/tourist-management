from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from models import db
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
migrate = Migrate(app, db)
JWTManager(app)
CORS(app)

from blueprints.auth import auth_bp
from blueprints.groups import groups_bp
from blueprints.routes_bp import routes_bp
from blueprints.applications import apps_bp
from blueprints.participants import parts_bp
from blueprints.finance import finance_bp
from blueprints.stats import stats_bp
from blueprints.logs import logs_bp
from blueprints.socket import socketio, init_socketio
from blueprints.agent import agent_bp

app.register_blueprint(auth_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(apps_bp)
app.register_blueprint(parts_bp)
app.register_blueprint(finance_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(agent_bp)

init_socketio(app)

# Swagger UI
swagger_bp = get_swaggerui_blueprint('/api/docs', '/api/swagger.json', config={'app_name': "智游云管 API"})
app.register_blueprint(swagger_bp)

SWAGGER_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "智游云管 API", "version": "1.0.0", "description": "旅游业务管理系统接口文档"},
    "servers": [{"url": "http://localhost:5000", "description": "本地开发"}],
    "components": {
        "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}
    },
    "security": [{"bearerAuth": []}],
    "paths": {
        "/api/login": {"post": {"tags": ["认证"], "summary": "登录获取Token",
            "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {
                "username": {"type": "string"}, "password": {"type": "string"}
            }, "required": ["username", "password"]}}}},
            "responses": {"200": {"description": "登录成功"}}}},
        "/api/tour_groups": {"get": {"tags": ["旅游团"], "summary": "获取已公开旅游团",
            "responses": {"200": {"description": "旅游团列表"}}}},
        "/api/routes": {"get": {"tags": ["路线"], "summary": "获取所有路线",
            "responses": {"200": {"description": "路线列表"}}}},
        "/api/applications": {"get": {"tags": ["申请"], "summary": "申请列表（分页）",
            "parameters": [
                {"name": "page", "in": "query", "schema": {"type": "integer"}},
                {"name": "per_page", "in": "query", "schema": {"type": "integer"}}
            ], "responses": {"200": {"description": "申请列表"}}}},
        "/api/stats": {"get": {"tags": ["统计"], "summary": "统计数据",
            "responses": {"200": {"description": "统计数据"}}}},
        "/api/audit_logs": {"get": {"tags": ["审计"], "summary": "操作日志",
            "responses": {"200": {"description": "日志列表"}}}},
        "/api/daily_export": {"get": {"tags": ["财务"], "summary": "财务导出",
            "parameters": [{"name": "date", "in": "query", "schema": {"type": "string"}}],
            "responses": {"200": {"description": "财务数据"}}}}
    }
}


@app.route('/api/swagger.json')
def swagger_json():
    return jsonify(SWAGGER_SPEC)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from models import User
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password_hash=generate_password_hash('admin123'),
                                display_name='王经理', role='admin'))
            db.session.commit()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, use_reloader=False)
