"""
集成测试：Login App Views
测试用户注册、登录、信息获取等认证相关功能的完整请求-响应流程
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from login.models import User as CustomUser


class LoginViewsIntegrationTest(APITestCase):
    """Login应用集成测试"""

    def setUp(self):
        self.client = APIClient()

        # 创建测试用户
        from utils.jwt import encrypt_password

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custom_user = CustomUser.objects.create(
            username='testuser',
            password=encrypt_password('testpass123'),
            nickname='测试用户'
        )

    def test_get_user_info_authenticated(self):
        """测试已登录用户获取信息"""
        # 使用JWT token认证
        from utils.jwt import generate_jwt
        token = generate_jwt({'user_id': self.custom_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get('/api/v1/user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_user_info_unauthenticated(self):
        """测试未登录用户获取信息"""
        response = self.client.get('/api/v1/user')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_info_by_id(self):
        """测试通过ID获取用户信息"""
        # 使用JWT token认证
        from utils.jwt import generate_jwt
        token = generate_jwt({'user_id': self.custom_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(f'/api/v1/user/{self.custom_user.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_user_success(self):
        """测试成功注册用户"""
        data = {
            'username': 'newuser123',
            'password': 'Testpass123-',  # 使用允许的特殊字符-而不是!
            'nickname': '新用户'
        }

        response = self.client.post(
            '/api/v1/register',
            data,
            format='json'
        )

        # API返回200，响应格式是{"message": "ok"}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'ok')

        # 验证用户已创建
        custom_user = CustomUser.objects.filter(username='newuser123').first()
        self.assertIsNotNone(custom_user)

    def test_register_user_duplicate_username(self):
        """测试注册重复用户名"""
        data = {
            'username': 'testuser',  # 已存在的用户名
            'password': 'newpass123',
            'email': 'new@example.com',
            'nickname': '新用户',
            'mobile': '13800138001'
        }

        response = self.client.post(
            '/api/v1/register',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # API返回格式是{"message": "..."}，没有code字段
        self.assertIn('message', response.data)

    def test_register_user_missing_fields(self):
        """测试注册时缺少必填字段"""
        data = {
            'username': 'newuser',
            # 缺少password
            'email': 'new@example.com'
        }

        response = self.client.post(
            '/api/v1/register',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_invalid_email(self):
        """测试注册时提供无效邮箱"""
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'invalid-email',  # 无效邮箱格式
            'nickname': '新用户'
        }

        response = self.client.post(
            '/api/v1/register',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """测试成功登录"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        # LoginView使用PATCH方法
        response = self.client.patch(
            '/api/v1/login',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_login_failure(self):
        """测试登录失败"""
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }

        response = self.client.patch(
            '/api/v1/login',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """测试登录时缺少必填字段"""
        data = {
            'username': 'testuser'
            # 缺少password
        }

        # LoginView使用PATCH方法
        response = self.client.patch(
            '/api/v1/login',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_success(self):
        """测试成功登出"""
        # 使用JWT token认证
        from utils.jwt import generate_jwt
        token = generate_jwt({'user_id': self.custom_user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.post('/api/v1/logout')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        """测试未登录用户登出"""
        response = self.client.post('/api/v1/logout')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
