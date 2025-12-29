import pytest
from unittest.mock import patch, MagicMock


# 认证标签：集成测试（通过 API 端点驱动，必要时 mock 外部依赖）
pytestmark = [pytest.mark.integration]

@pytest.mark.django_db
class TestConsumptionFlow:
    """
    集成测试：消费记录获取
    """

    def test_bind_idserial(self, auth_client):
        """测试绑定学号"""
        url = '/api/v1/canteen/bind/'
        data = {
            'idserial': '2023000001',
            'browser_type': 'chrome'
        }
        
        # mock canteen.views.bind_idserial_and_fetch
        with patch('canteen.views.bind_idserial_and_fetch') as mock_bind:
            mock_bind.return_value = (True, "绑定成功", {'idserial': '2023000001'})
            
            response = auth_client.post(url, data, format='json')
            
            assert response.status_code == 200
            assert response.data['code'] == 200
            assert response.data['message'] == "绑定成功"

    def test_get_consumption(self, auth_client, test_user):
        """测试获取消费记录"""
        # Mock get_user_consumption to return data
        # 使用简单对象代替 MagicMock，避免 DRF 序列化器内省导致的问题
        class MockConsumption:
            id = 1
            username = 'testuser'
            idserial = '2021000001'
            total_amount = 100.0
            canteen_count = 5
            canteen_data = {}
            last_fetched = '2023-01-01'
            created = '2023-01-01'

        with patch('canteen.views.get_user_consumption') as mock_get:
            mock_get.return_value = MockConsumption()
            
            url = '/api/v1/canteen/consumption/'
            response = auth_client.get(url)
            
            assert response.status_code == 200
            assert response.data['data']['idserial'] == '2021000001'

    def test_unbind_consumption(self, auth_client, test_user):
        """测试解绑消费记录"""
        # Mock unbind_consumption
        with patch('canteen.views.unbind_consumption') as mock_unbind:
            mock_unbind.return_value = (True, "解绑成功")
            
            url = '/api/v1/canteen/unbind/'
            # The view uses DELETE method
            response = auth_client.delete(url)
            
            assert response.status_code == 200
            assert response.data['message'] == "解绑成功"
