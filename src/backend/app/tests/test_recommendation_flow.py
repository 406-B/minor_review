import pytest
from list.models import Dish, Tag


# 认证标签：集成测试（通过 API + DB 链路验证）
pytestmark = [pytest.mark.integration]

@pytest.mark.django_db
class TestRecommendationFlow:
    """
    集成测试：个性化推荐链路
    """

    def test_set_preference_tags(self, auth_client, test_user, sample_tag):
        """测试设置偏好标签"""
        url = '/api/v1/profile/preference-tags/set'
        data = {
            'tag_ids': [sample_tag.id]
        }
        
        response = auth_client.post(url, data, format='json')
        assert response.status_code == 200
        assert response.data['code'] == 200
        
        # 验证数据库
        # test_user 是 auth.User，没有 preference_tags 字段
        # 需要查询 login.models.User
        from login.models import User
        login_user = User.objects.get(username=test_user.username)
        assert login_user.preference_tags.filter(id=sample_tag.id).exists()

    def test_get_recommended_dishes_no_tags(self, auth_client):
        """测试未设置标签时获取推荐（应返回404）"""
        url = '/api/v1/profile/recommended-dishes'
        response = auth_client.get(url)
        
        assert response.status_code == 404
        assert response.data['code'] == 404

    def test_get_recommended_dishes_pref_mode(self, auth_client, test_user, sample_dish, sample_tag):
        """测试按偏好推荐模式"""
        # 1. 设置偏好标签
        from login.models import User
        login_user = User.objects.get(username=test_user.username)
        login_user.preference_tags.add(sample_tag)
        
        # 2. 确保 sample_dish 包含该标签 (conftest.py 中已添加)
        
        url = '/api/v1/profile/recommended-dishes?mode=pref'
        response = auth_client.get(url)
        
        assert response.status_code == 200
        assert response.data['code'] == 200
        dishes = response.data['data']['dishes']
        assert len(dishes) > 0
        assert dishes[0]['id'] == sample_dish.id

    def test_get_recommended_dishes_mix_mode(self, auth_client, test_user, sample_dish, sample_tag):
        """测试综合推荐模式"""
        # 1. 设置偏好标签
        from login.models import User
        login_user = User.objects.get(username=test_user.username)
        login_user.preference_tags.add(sample_tag)
        
        # 2. 增加热度（模拟）
        sample_dish.view_count = 100
        sample_dish.save()
        
        url = '/api/v1/profile/recommended-dishes?mode=mix'
        response = auth_client.get(url)
        
        assert response.status_code == 200
        assert response.data['code'] == 200
        dishes = response.data['data']['dishes']
        assert len(dishes) > 0
        # 综合模式下，该菜品既匹配标签又有热度，应该在列表中
        dish_ids = [d['id'] for d in dishes]
        assert sample_dish.id in dish_ids

    def test_add_preference_tags(self, auth_client, test_user, sample_tag):
        """测试添加偏好标签（追加模式）"""
        # 1. 先设置一个标签
        from login.models import User
        login_user = User.objects.get(username=test_user.username)
        login_user.preference_tags.add(sample_tag)
        
        # 2. 创建另一个标签
        other_tag = Tag.objects.create(name="甜")
        
        url = '/api/v1/profile/preference-tags/add'
        data = {
            'tag_ids': [other_tag.id]
        }
        
        response = auth_client.post(url, data, format='json')
        assert response.status_code == 200
        
        # 验证两个标签都存在
        assert login_user.preference_tags.count() == 2
        assert login_user.preference_tags.filter(id=sample_tag.id).exists()
        assert login_user.preference_tags.filter(id=other_tag.id).exists()

    def test_recommendation_sorting(self, auth_client, test_user, sample_tag, sample_canteen):
        """测试推荐结果排序：匹配度 > 评分 > 热度"""
        from login.models import User
        login_user = User.objects.get(username=test_user.username)
        login_user.preference_tags.add(sample_tag)
        
        # 菜品A: 匹配标签, 评分 5.0
        dish_a = Dish.objects.create(name="A", canteen=sample_canteen, price=10, rating=5.0)
        dish_a.tags.add(sample_tag)
        
        # 菜品B: 匹配标签, 评分 3.0
        dish_b = Dish.objects.create(name="B", canteen=sample_canteen, price=10, rating=3.0)
        dish_b.tags.add(sample_tag)
        
        # 菜品C: 不匹配标签
        dish_c = Dish.objects.create(name="C", canteen=sample_canteen, price=10, rating=5.0)
        
        url = '/api/v1/profile/recommended-dishes?mode=pref'
        response = auth_client.get(url)
        
        dishes = response.data['data']['dishes']
        # C 不应该在推荐列表中 (pref mode 只返回匹配的)
        dish_ids = [d['id'] for d in dishes]
        assert dish_c.id not in dish_ids
        
        # A 应该在 B 前面 (评分高)
        # 注意：dishes 列表可能包含 sample_dish (如果它也匹配标签)
        # 我们只关心 A 和 B 的相对顺序
        a_index = -1
        b_index = -1
        for i, d in enumerate(dishes):
            if d['id'] == dish_a.id:
                a_index = i
            elif d['id'] == dish_b.id:
                b_index = i
        
        assert a_index != -1
        assert b_index != -1
        assert a_index < b_index
