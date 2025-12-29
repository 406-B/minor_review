import pytest
from login.models import User
from django.contrib.auth.models import User as AuthUser
from utils.jwt import encrypt_password


# 认证标签：集成测试（通过 API + DB 链路验证）
pytestmark = [pytest.mark.integration]

@pytest.mark.django_db
class TestLoginFlow:
    """
    集成测试：用户登录注册流程
    """

    @pytest.fixture
    def api_client(self):
        from rest_framework.test import APIClient
        return APIClient()

    def test_register_success(self, api_client):
        """测试用户注册成功"""
        url = '/api/v1/register'
        # 修正：符合 register_params_check 的规则
        # 用户名：5-12 位，以字母开头且包含数字 -> user123
        # 密码：8-15 位，需包含大小写/数字/特殊字符 -_*^ -> Password123-
        data = {
            'username': 'user123',
            'password': 'Password123-',
            'confirm_password': 'Password123-',
            'nickname': 'New User'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        assert response.data['message'] == "ok"
        
        # 验证数据库
        assert User.objects.filter(username='user123').exists()

    def test_register_duplicate_username(self, api_client):
        """测试重复用户名注册"""
        # 先创建一个用户
        User.objects.create(
            username='user123',
            password=encrypt_password('Password123-'),
            nickname='Existing User'
        )
        
        url = '/api/v1/register'
        data = {
            'username': 'user123',
            'password': 'Password123-',
            'confirm_password': 'Password123-',
            'nickname': 'Another User'
        }
        
        response = api_client.post(url, data, format='json')
        
        # Duplicate username returns 400 with '用户名已存在'
        assert response.status_code == 400
        assert response.data['message'] == "用户名已存在"

    def test_login_success(self, api_client):
        """测试用户登录成功"""
        username = 'loginuser'
        password = 'password123'
        encrypted_pwd = encrypt_password(password)
        
        User.objects.create(
            username=username,
            password=encrypted_pwd,
            nickname='Login User'
        )
        
        url = '/api/v1/login'
        data = {
            'username': username,
            'password': password
        }
        
        # LoginView uses PATCH method
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == 200
        assert 'jwt' in response.data

    def test_login_wrong_password(self, api_client):
        """测试密码错误登录"""
        username = 'loginuser'
        password = 'password123'
        encrypted_pwd = encrypt_password(password)
        
        User.objects.create(
            username=username,
            password=encrypted_pwd,
            nickname='Login User'
        )
        
        url = '/api/v1/login'
        data = {
            'username': username,
            'password': 'wrongpassword'
        }
        
        # LoginView uses PATCH method
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == 401
        assert response.data['message'] == "Invalid credentials"

    def test_get_user_info(self, api_client):
        """测试获取用户信息"""
        from utils.jwt import generate_jwt
        
        username = 'infouser'
        password = 'password123'
        
        user = User.objects.create(
            username=username,
            password=encrypt_password(password),
            nickname='Info User'
        )
        
        # 生成 Token
        payload = {'user_id': user.id, 'username': user.username}
        token = generate_jwt(payload)
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 修正：根据 login/urls.py，路径应该是 /api/v1/user
        url = '/api/v1/user'
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.data['username'] == username
        assert response.data['nickname'] == 'Info User'
