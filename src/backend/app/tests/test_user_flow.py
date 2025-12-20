import pytest
from django.urls import reverse
from login.models import User as LoginUser
from django.contrib.auth.models import User as AuthUser

@pytest.mark.django_db
class TestUserFlow:
    """
    集成测试：用户相关链路
    """

    def test_register_user(self, api_client):
        """测试用户注册"""
        url = '/api/v1/register'
        # 根据 register_params_check.py 调整参数
        # 用户名：5-12 位，以字母开头且包含数字 -> 'newuser1'
        # 密码：8-15 位，需包含大小写/数字/特殊字符 -_*^ -> 'Password123-'
        data = {
            'username': 'newuser1',
            'password': 'Password123-',
            'nickname': 'New User'
        }
        response = api_client.post(url, data, format='json')
        if response.status_code == 400:
            print(response.data)
        assert response.status_code == 200
        # register_user 返回 Response({'message': 'ok'}, status=200)
        assert response.data['message'] == 'ok'
        assert LoginUser.objects.filter(username='newuser1').exists()

    def test_login_user(self, api_client, test_user):
        """测试用户登录"""
        # 确保 login.models.User 存在
        from utils.jwt import encrypt_password
        if not LoginUser.objects.filter(username=test_user.username).exists():
            LoginUser.objects.create(
                username=test_user.username,
                password=encrypt_password('Password123-'), # 密码需要加密存储
                nickname='Test User'
            )
        
        url = '/api/v1/login'
        data = {
            'username': test_user.username,
            'password': 'Password123-'
        }
        # LoginView 使用 PATCH 方法而不是 POST
        response = api_client.patch(url, data, format='json')
        assert response.status_code == 200
        # LoginView 返回 {'jwt': ..., 'userId': ..., ...}
        assert 'jwt' in response.data

    def test_get_user_info(self, auth_client, test_user):
        """测试获取用户信息"""
        url = '/api/v1/user'
        response = auth_client.get(url)
        assert response.status_code == 200
        # get_user_info 直接返回 Response(data)，没有包装 code
        assert response.data['username'] == test_user.username

    def test_get_profile(self, auth_client, test_user):
        """测试获取个人资料"""
        url = '/api/v1/profile'
        response = auth_client.get(url)
        assert response.status_code == 200
        # get_profile 直接返回 Response(serializer.data)，没有包装 code
        assert response.data['username'] == test_user.username

    def test_update_profile(self, auth_client, test_user):
        """测试更新个人资料"""
        url = '/api/v1/profile/update'
        data = {
            'nickname': 'Updated Nickname'
        }
        # update_profile uses PUT or PATCH
        response = auth_client.patch(url, data, format='json')
        assert response.status_code == 200
        # update_profile returns {'message': ..., 'data': ...}
        assert response.data['data']['nickname'] == 'Updated Nickname'
        
        # Verify DB update
        from login.models import User
        user = User.objects.get(username=test_user.username)
        assert user.nickname == 'Updated Nickname'

    def test_update_password(self, auth_client, test_user):
        """测试修改密码"""
        url = '/api/v1/profile/password'
        data = {
            'old_password': 'password123',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        
        # update_password uses POST
        response = auth_client.post(url, data, format='json')
        assert response.status_code == 200
        assert response.data['message'] == '密码修改成功'
        
        # Verify login with new password
        # 注意：auth_client 使用的 token 是基于旧密码生成的，但 JWT 验证通常只校验签名和有效期，不校验密码是否变更
        # 除非有黑名单机制。这里我们尝试用新密码登录来验证
        
        login_url = '/api/v1/login'
        login_data = {
            'username': test_user.username,
            'password': 'NewPassword123!'
        }
        # LoginView uses PATCH
        response = auth_client.patch(login_url, login_data, format='json')
        assert response.status_code == 200
        assert 'jwt' in response.data

    def test_get_user_stats(self, auth_client):
        """测试获取用户统计信息"""
        url = '/api/v1/profile/stats'
        response = auth_client.get(url)
        assert response.status_code == 200
        # 验证返回结构
        # 根据 profile/controllers.py 的实现，返回的字段是 comments_count 而不是 commented_posts_count
        assert 'liked_posts_count' in response.data
        assert 'comments_count' in response.data
        assert 'posts_count' in response.data
        assert 'following_count' in response.data
