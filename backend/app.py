from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
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

app.register_blueprint(auth_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(apps_bp)
app.register_blueprint(parts_bp)
app.register_blueprint(finance_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(logs_bp)

init_socketio(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from models import User
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password_hash=generate_password_hash('admin123'),
                                display_name='王经理', role='admin'))
            db.session.commit()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, use_reloader=False)
