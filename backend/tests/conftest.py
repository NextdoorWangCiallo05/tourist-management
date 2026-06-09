import os
# Override DB to in-memory BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import pytest
from app import app as flask_app
from models import db as _db
from werkzeug.security import generate_password_hash


@pytest.fixture(autouse=True)
def app():
    """Create a clean in-memory database for each test."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['JWT_SECRET_KEY'] = 'test_jwt_key'
    
    with flask_app.app_context():
        _db.create_all()
        from models import User
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            display_name='管理员',
            role='admin',
            email='admin@test.com',
            phone='13800138000'
        )
        _db.session.add(admin)
        _db.session.commit()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Database session within app context."""
    with app.app_context():
        yield _db


def login(client, username='admin', password='admin123'):
    """Helper: login and return access_token."""
    resp = client.post('/api/login', json={
        'username': username,
        'password': password
    })
    data = resp.get_json()
    if data.get('code') == 200:
        return data['data']['access_token']
    return None


@pytest.fixture
def auth_headers(client):
    """Fixture: get JWT auth headers."""
    token = login(client)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def seed_data(db):
    """Seed test data: routes + tour groups."""
    from models import Route, TourGroup
    from datetime import date, timedelta
    
    route = Route(route_code='RT001', route_name='云南大理丽江经典5日游',
                  description='测试路线', is_active=True, version=1)
    db.session.add(route)
    db.session.flush()
    
    group = TourGroup(
        group_code='TG001', route_id=route.id,
        departure_date=date.today() + timedelta(days=60),
        deadline_date=date.today() + timedelta(days=50),
        max_capacity=30, adult_price=3999.0, child_price=1999.0,
        is_public=True
    )
    db.session.add(group)
    db.session.commit()
    return {'route': route, 'group': group}
