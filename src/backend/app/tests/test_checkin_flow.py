import pytest
from list.models import DishCheckInRecord, UserDishHistory
from django.utils import timezone


# 认证标签：集成测试（通过 API + DB 链路验证）
pytestmark = [pytest.mark.integration]

@pytest.mark.django_db
class TestCheckInFlow:
    """
    集成测试：打卡与美食日历链路
    """

    def test_check_in_dish(self, auth_client, sample_dish):
        """测试菜品打卡"""
        url = f'/api/v1/dishes/{sample_dish.id}/check-in/'
        data = {
            'notes': '今天吃得很开心'
        }
        
        response = auth_client.post(url, data, format='json')
        assert response.status_code == 200
        assert response.data['code'] == 200
        
        # 验证打卡记录
        assert DishCheckInRecord.objects.filter(dish=sample_dish, notes='今天吃得很开心').exists()
        # 验证历史统计
        history = UserDishHistory.objects.get(dish=sample_dish)
        assert history.count == 1

    def test_check_in_dish_daily_limit_exceeded_returns_400(self, auth_client, sample_dish):
        """同一道菜每日最多打卡3次，超过返回 400（覆盖 check_in_dish 上限分支）。"""
        url = f'/api/v1/dishes/{sample_dish.id}/check-in/'

        # 前三次成功
        for i in range(3):
            resp = auth_client.post(url, {'notes': f'n{i}'}, format='json')
            assert resp.status_code == 200
            assert resp.data['code'] == 200

        # 第四次应触发上限
        resp4 = auth_client.post(url, {'notes': 'n3'}, format='json')
        assert resp4.status_code == 400
        assert resp4.data['code'] == 400

    def test_get_food_calendar(self, auth_client, sample_dish):
        """测试获取美食日历"""
        # 先打卡一次
        self.test_check_in_dish(auth_client, sample_dish)
        
        # 测试 get_check_in_history (按日期范围)
        url = '/api/v1/profile/check-in-history'
        response = auth_client.get(url)
        
        assert response.status_code == 200
        assert response.data['code'] == 200
        data = response.data['data']
        assert 'check_ins' in data
        assert len(data['check_ins']) > 0
        assert data['summary']['total_check_ins'] >= 1

        # 测试 get_check_in_calendar (按月概览)
        now = timezone.now()
        url_calendar = f'/api/v1/profile/check-in-calendar?year={now.year}&month={now.month}'
        response_calendar = auth_client.get(url_calendar)
        
        assert response_calendar.status_code == 200
        assert response_calendar.data['code'] == 200
        data_calendar = response_calendar.data['data']
        assert data_calendar['year'] == now.year
        assert data_calendar['month'] == now.month
        assert len(data_calendar['check_in_dates']) > 0

        # 测试 list/views.py 中的 get_food_calendar (旧接口，但仍在 list/urls.py 中)
        url_old = '/api/v1/user/food-calendar/'
        response_old = auth_client.get(url_old)
        assert response_old.status_code == 200
        assert response_old.data['code'] == 200

    def test_get_user_achievements(self, auth_client, sample_dish):
        """测试获取用户成就"""
        # 打卡多次以触发成就（假设逻辑）
        # 这里只测试接口连通性
        url = '/api/v1/user/achievements/'
        response = auth_client.get(url)
        
        assert response.status_code == 200
        assert response.data['code'] == 200
