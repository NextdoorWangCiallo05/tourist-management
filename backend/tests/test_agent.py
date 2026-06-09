"""Tests for AI Agent (rule engine)."""


class TestAgentRuleEngine:
    """测试 AI 助手的规则引擎（无需 API Key）"""

    def test_chat_tour_groups(self, client, auth_headers, seed_data):
        """'查旅游团' 应返回旅游团列表"""
        resp = client.post('/api/agent/chat', json={
            'message': '查旅游团'
        }, headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200
        assert data['data']['mode'] == 'rule'
        assert '旅游团' in data['data']['reply']

    def test_chat_stats(self, client, auth_headers):
        """'系统概览' 应返回统计信息"""
        resp = client.post('/api/agent/chat', json={
            'message': '系统概览'
        }, headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200
        assert data['data']['mode'] == 'rule'
        assert '系统概览' in data['data']['reply']

    def test_chat_cancel_fee(self, client, auth_headers):
        """'取消手续费' 应返回规则"""
        resp = client.post('/api/agent/chat', json={
            'message': '取消手续费怎么算'
        }, headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200
        assert data['data']['mode'] == 'rule'
        assert '免费' in data['data']['reply'] or 'Free' in data['data']['reply']
        # 应包含四个档位
        assert '30' in data['data']['reply']

    def test_chat_anomalies(self, client, auth_headers):
        """'异常检测' 应返回检测结果"""
        resp = client.post('/api/agent/chat', json={
            'message': '异常检测'
        }, headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200
        assert data['data']['mode'] == 'rule'

    def test_chat_fallback(self, client, auth_headers):
        """无法识别的输入应返回帮助提示"""
        resp = client.post('/api/agent/chat', json={
            'message': '今天天气怎么样'
        }, headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200
        # 无 API Key 时应返回 fallback 提示
        assert '试试这样问' in data['data']['reply'] or 'try' in data['data']['reply'].lower()

    def test_chat_empty_message(self, client, auth_headers):
        """空消息应返回提示"""
        resp = client.post('/api/agent/chat', json={
            'message': ''
        }, headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200

    def test_anomalies_api(self, client, auth_headers):
        """GET /api/agent/anomalies 应返回列表"""
        resp = client.get('/api/agent/anomalies', headers=auth_headers)
        data = resp.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
