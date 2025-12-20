import pytest
from django.urls import reverse
from list.models import Dish

@pytest.mark.django_db
class TestCanteenFlow:
    """
    集成测试：食堂与菜品浏览链路
    """

    def test_get_canteen_list(self, api_client, sample_canteen):
        """测试获取食堂列表"""
        url = reverse('list:canteen-list')
        
        response = api_client.get(url)
        
        assert response.status_code == 200
        # 修正：后端返回结构是 {'code': 200, 'message': '...', 'data': [...]}
        assert len(response.data['data']) >= 1
        assert response.data['data'][0]['name'] == sample_canteen.name

    def test_search_dish_by_name(self, api_client, sample_dish):
        """测试按名称搜索菜品"""
        # 搜索存在的菜品
        response = api_client.get('/api/v1/dishes/', {'search': '麻婆'})  # <-- Use 'search' param
        assert response.status_code == 200
        # dish_list 返回 {'code': 200, 'data': [...]}
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['name'] == '麻婆豆腐'

        # 搜索不存在的菜品
        response = api_client.get('/api/v1/dishes/', {'search': '不存在的菜'})
        assert response.status_code == 200
        assert len(response.data['data']) == 0

    def test_search_dish_by_tag(self, api_client, sample_dish, sample_tag):
        """测试按标签搜索菜品"""
        # 假设后端支持 tag_ids 参数
        response = api_client.get('/api/v1/dishes/', {'tag_ids': sample_tag.id})
        assert response.status_code == 200
        assert len(response.data['data']) >= 1
        assert response.data['data'][0]['id'] == sample_dish.id

    def test_dish_detail(self, api_client, sample_dish):
        """测试获取菜品详情"""
        url = f'/api/v1/dishes/{sample_dish.id}/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        # dish_detail 返回 {'code': 200, 'data': {...}}
        assert response.data['data']['name'] == sample_dish.name
        assert response.data['data']['price'] == '12.50'  # Decimal 序列化通常是字符串
