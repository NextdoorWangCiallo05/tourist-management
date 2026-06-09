"""Tests for authentication API (login, register, user management)."""


class TestLogin:
    def test_login_success(self, client):
        """正确账号密码应返回 token"""
        resp = client.post('/api/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['code'] == 200
        assert data['data']['access_token'] is not None
        assert data['data']['role'] == 'admin'

    def test_login_wrong_password(self, client):
        """错误密码应返回 401"""
        resp = client.post('/api/login', json={
            'username': 'admin',
            'password': 'wrong_password'
        })
        data = resp.get_json()
        assert resp.status_code == 401
        assert data['code'] == 401

    def test_login_empty_fields(self, client):
        """空用户名密码"""
        resp = client.post('/api/login', json={
            'username': '',
            'password': ''
        })
        assert resp.status_code == 401


class TestRegister:
    def test_register_success(self, client):
        """注册新用户应成功并返回 token 自动登录"""
        resp = client.post('/api/register', json={
            'username': 'testuser',
            'display_name': '测试用户',
            'email': 'test@example.com',
            'phone': '13912345678',
            'password': 'test123456',
            'confirm_password': 'test123456'
        })
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['code'] == 200
        assert data['data']['access_token'] is not None
        assert data['data']['role'] == 'operator'

    def test_register_duplicate_username(self, client):
        """重复用户名应失败"""
        resp = client.post('/api/register', json={
            'username': 'admin',
            'password': 'test123456',
            'confirm_password': 'test123456'
        })
        data = resp.get_json()
        assert data['code'] != 200  # 400 用户名已存在

    def test_register_password_mismatch(self, client):
        """两次密码不一致应失败"""
        resp = client.post('/api/register', json={
            'username': 'newuser',
            'password': 'test123456',
            'confirm_password': 'different'
        })
        data = resp.get_json()
        assert data['code'] != 200

    def test_register_invalid_email(self, client):
        """邮箱格式不正确应失败"""
        resp = client.post('/api/register', json={
            'username': 'user2',
            'password': 'test123456',
            'confirm_password': 'test123456',
            'email': 'not-an-email'
        })
        data = resp.get_json()
        assert data['code'] != 200

    def test_register_short_password(self, client):
        """密码少于6位应失败"""
        resp = client.post('/api/register', json={
            'username': 'user3',
            'password': '12345',
            'confirm_password': '12345'
        })
        data = resp.get_json()
        assert data['code'] != 200


class TestUserManagement:
    def test_list_users_as_admin(self, client, auth_headers):
        """管理员应能查看用户列表"""
        resp = client.get('/api/users', headers=auth_headers)
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['code'] == 200
        assert len(data['data']) >= 1
        assert any(u['username'] == 'admin' for u in data['data'])

    def test_list_users_without_auth(self, client):
        """未登录不能查看用户列表"""
        resp = client.get('/api/users')
        assert resp.status_code == 401

    def test_list_users_as_operator(self, client):
        """操作员不能查看用户列表"""
        # 注册操作员
        resp = client.post('/api/register', json={
            'username': 'operator1',
            'password': 'test123456',
            'confirm_password': 'test123456'
        })
        token = resp.get_json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        resp = client.get('/api/users', headers=headers)
        data = resp.get_json()
        assert data['code'] != 200  # 403
