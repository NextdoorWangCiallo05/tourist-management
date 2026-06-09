"""Tests for application API (create, deposit, complete, cancel)."""


class TestCreateApplication:
    def test_create_success(self, client, auth_headers, seed_data):
        """创建申请（含2名参加者）应成功"""
        payload = {
            'group_id': seed_data['group'].id,
            'responsible_name': '张三',
            'phone_number': '13800138000',
            'adult_count': 2,
            'child_count': 0,
            'participants': [
                {'name': '张三', 'id_number': '110101199001011234', 'is_adult': True},
                {'name': '李四', 'id_number': '110101199002021234', 'is_adult': True}
            ]
        }
        resp = client.post('/api/applications', json=payload, headers=auth_headers)
        data = resp.get_json()
        assert resp.status_code == 201
        assert data['code'] == 201
        assert data['data']['application_no'].startswith('AP')
        assert data['data']['deposit_amount'] > 0

    def test_create_without_participants(self, client, auth_headers, seed_data):
        """创建申请（无参加者）也应成功"""
        payload = {
            'group_id': seed_data['group'].id,
            'responsible_name': '王五',
            'phone_number': '13900139000',
            'adult_count': 1,
            'child_count': 0
        }
        resp = client.post('/api/applications', json=payload, headers=auth_headers)
        assert resp.status_code == 201

    def test_create_invalid_group(self, client, auth_headers):
        """不存在的旅游团应返回404"""
        payload = {
            'group_id': 9999,
            'responsible_name': '测试',
            'phone_number': '13800138000',
            'adult_count': 1,
            'child_count': 0
        }
        resp = client.post('/api/applications', json=payload, headers=auth_headers)
        assert resp.status_code == 404


class TestApplicationFlow:
    """完整流程：创建→支付订金→完成"""

    def _create_app(self, client, auth_headers, seed_data) -> str:
        payload = {
            'group_id': seed_data['group'].id,
            'responsible_name': '赵六',
            'phone_number': '13700137000',
            'adult_count': 1,
            'child_count': 0,
            'participants': [
                {'name': '赵六', 'id_number': '110101199003031234', 'is_adult': True}
            ]
        }
        resp = client.post('/api/applications', json=payload, headers=auth_headers)
        return resp.get_json()['data']['application_no']

    def test_pay_deposit(self, client, auth_headers, seed_data):
        """支付订金"""
        app_no = self._create_app(client, auth_headers, seed_data)
        
        # 先查看详情获取订金金额
        detail = client.get(f'/api/applications/{app_no}', headers=auth_headers)
        deposit = detail.get_json()['data']['deposit_amount']
        
        resp = client.post(f'/api/applications/{app_no}/deposit', 
                          json={'amount_paid': deposit}, headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200

    def test_complete_application(self, client, auth_headers, seed_data):
        """完成申请（需先支付订金且参加者齐全）"""
        app_no = self._create_app(client, auth_headers, seed_data)
        
        # 支付订金
        detail = client.get(f'/api/applications/{app_no}', headers=auth_headers)
        deposit = detail.get_json()['data']['deposit_amount']
        client.post(f'/api/applications/{app_no}/deposit',
                   json={'amount_paid': deposit}, headers=auth_headers)
        
        # 完成申请
        resp = client.post(f'/api/applications/{app_no}/complete', headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200

    def test_cancel_application(self, client, auth_headers, seed_data):
        """取消申请"""
        app_no = self._create_app(client, auth_headers, seed_data)
        
        resp = client.post(f'/api/applications/{app_no}/cancel', headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200
        assert 'cancellation_fee' in data['data']
        assert 'refund_amount' in data['data']
