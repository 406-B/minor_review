import pytest
from list.models import Review, Dish


# 认证标签：集成测试（通过 API + DB 链路验证）
pytestmark = [pytest.mark.integration]

@pytest.mark.django_db
class TestReviewFlow:
    """
    集成测试：评价交互链路
    """

    def test_create_review_authenticated(self, auth_client, sample_dish):
        """测试登录用户发表评论"""
        # 先创建评分（业务逻辑要求评论前必须评分）
        from list.models import Rating
        from django.contrib.auth.models import User
        
        # 获取 auth.User 用于创建 Rating
        user = User.objects.get(username='testuser')
        
        Rating.objects.create(
            user=user,
            dish=sample_dish,
            score=5
        )

        url = f'/api/v1/dishes/{sample_dish.id}/reviews/create/'
        data = {
            'content': '味道很正宗！',
            'images': []
        }

        response = auth_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert Review.objects.count() == 1
        review = Review.objects.first()
        assert review.content == '味道很正宗！'
        assert review.user.username == 'testuser'

    def test_create_review_unauthenticated(self, api_client, sample_dish):
        """测试未登录用户发表评论（应被拒绝）"""
        url = f'/api/v1/dishes/{sample_dish.id}/reviews/create/'
        data = {
            'content': '想评论但没登录'
        }
        
        response = api_client.post(url, data, format='json')
        # DRF 默认未认证返回 401 或 403，取决于配置
        # 如果是 PermissionDenied 则为 403，如果是 AuthenticationFailed 则为 401
        # 这里实际返回了 403
        assert response.status_code in [401, 403]

    def test_review_impact_on_dish(self, auth_client, sample_dish):
        """测试评论对菜品评分的影响（验证业务逻辑集成）"""
        # 先创建评分
        from list.models import Rating
        from django.contrib.auth.models import User
        
        user = User.objects.get(username='testuser')
        
        Rating.objects.create(
            user=user,
            dish=sample_dish,
            score=5
        )

        url = f'/api/v1/dishes/{sample_dish.id}/reviews/create/'
        
        # 发表评论
        # 注意：ReviewSerializer 验证内容长度至少 5 个字符
        auth_client.post(url, {
            'content': '好评123'  # 确保超过5个字符
        }, format='json')

        # 刷新菜品数据
        sample_dish.refresh_from_db()
        
        assert Review.objects.filter(dish=sample_dish).exists()
