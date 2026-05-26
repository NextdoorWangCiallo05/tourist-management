from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    route_code = db.Column(db.String(50), unique=True, nullable=False)
    route_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)

class TourGroup(db.Model):
    __tablename__ = 'tour_groups'
    id = db.Column(db.Integer, primary_key=True)
    group_code = db.Column(db.String(50), unique=True, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    deadline_date = db.Column(db.Date, nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    adult_price = db.Column(db.Float, nullable=False)
    child_price = db.Column(db.Float, nullable=False)
    discount_rate = db.Column(db.Float, default=0.0)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    route = db.relationship('Route', backref=db.backref('tour_groups', lazy=True))

class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    id = db.Column(db.Integer, primary_key=True)
    tour_group_id = db.Column(db.Integer, db.ForeignKey('tour_groups.id'), nullable=False)
    adult_price = db.Column(db.Float, nullable=False)
    child_price = db.Column(db.Float, nullable=False)
    discount_rate = db.Column(db.Float, default=0.0)
    effective_date = db.Column(db.DateTime, default=datetime.now)
    
    tour_group = db.relationship('TourGroup', backref=db.backref('price_history', lazy=True))

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    application_no = db.Column(db.String(50), unique=True, nullable=False)
    tour_group_id = db.Column(db.Integer, db.ForeignKey('tour_groups.id'), nullable=False)
    responsible_name = db.Column(db.String(100), nullable=False)
    responsible_phone = db.Column(db.String(20), nullable=False)
    adult_count = db.Column(db.Integer, nullable=False, default=0)
    child_count = db.Column(db.Integer, nullable=False, default=0)
    deposit_amount = db.Column(db.Float, default=0.0)
    deposit_paid = db.Column(db.Boolean, default=False)
    balance_amount = db.Column(db.Float, default=0.0)
    balance_paid = db.Column(db.Boolean, default=False)
    balance_due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    tour_group = db.relationship('TourGroup', backref=db.backref('applications', lazy=True))

class Participant(db.Model):
    __tablename__ = 'participants'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    id_type = db.Column(db.String(20), default='身份证')
    id_number = db.Column(db.String(50))
    is_adult = db.Column(db.Boolean, default=True)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    email = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_relation = db.Column(db.String(50))
    emergency_contact_address = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(20))
    is_responsible = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')
    
    application = db.relationship('Application', backref=db.backref('participants', lazy=True))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(50), default='操作员')
    role = db.Column(db.String(20), default='operator')
    created_at = db.Column(db.DateTime, default=datetime.now)

class RouteHistory(db.Model):
    __tablename__ = 'route_history'
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    route_code = db.Column(db.String(50), nullable=False)
    route_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, default=datetime.now)
    change_type = db.Column(db.String(20))
    
    route = db.relationship('Route', backref=db.backref('route_history', lazy=True))

class PaymentRecord(db.Model):
    __tablename__ = 'payment_records'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.now)
    
    application = db.relationship('Application', backref=db.backref('payment_records', lazy=True))

class SystemConfig(db.Model):
    __tablename__ = 'system_config'
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(50), unique=True, nullable=False)
    config_value = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200))


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.String(50))
    detail = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.now)