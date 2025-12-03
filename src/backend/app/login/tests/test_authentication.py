"""
集成测试：用户认证流程
测试注册、登录、登出等完整流程
"""
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from login.models import User as CustomUser
from utils.jwt import encrypt_password, verify_jwt


class AuthenticationFlowTest(APITestCase):
    """认证流程集成测试"""

    def setUp(self):
        self.client = APIClient()

    def test_register_login_flow(self):
        """测试注册-登录完整流程"""
        # 1. 注册用户
        register_data = {
            'username': 'newuser',
            'password': 'password123',
            'nickname': '新用户'
        }
        response = self.client.post(
            '/api/register/',
            register_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. 使用注册的凭证登录
        login_data = {
            'username': 'newuser',
            'password': 'password123'
        }
        response = self.client.patch(
            '/api/login/',
            login_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data)

        jwt_token = response.data['jwt']

        # 3. 使用JWT访问受保护资源
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_token}')
        response = self.client.get('/api/user/info/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'newuser')

    def test_invalid_login_credentials(self):
        """测试错误凭证登录"""
        # 先注册用户
        CustomUser.objects.create(
            username='testuser',
            password=encrypt_password('correctpass'),
            nickname='测试'
        )

        # 使用错误密码登录
        response = self.client.patch(
            '/api/login/',
            {
                'username': 'testuser',
                'password': 'wrongpass'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """测试登录不存在的用户"""
        response = self.client.patch(
            '/api/login/',
            {
                'username': 'nonexistent',
                'password': 'anypass'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_duplicate_username(self):
        """测试注册重复用户名"""
        # 第一次注册
        self.client.post(
            '/api/register/',
            {
                'username': 'duplicate',
                'password': 'pass123',
                'nickname': '用户1'
            },
            format='json'
        )

        # 尝试用相同用户名注册
        response = self.client.post(
            '/api/register/',
            {
                'username': 'duplicate',
                'password': 'pass456',
                'nickname': '用户2'
            },
            format='json'
        )

        # 应该失败
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])

    def test_register_missing_fields(self):
        """测试注册缺少必需字段"""
        # 缺少密码
        response = self.client.post(
            '/api/register/',
            {
                'username': 'newuser',
                'nickname': '新用户'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """测试登出"""
        # 先登录
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=user)

        # 登出
        response = self.client.post('/api/logout/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_resource_without_auth(self):
        """测试未认证访问受保护资源"""
        response = self.client.get('/api/user/info/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_contains_user_info(self):
        """测试JWT包含用户信息"""
        # 注册并登录
        self.client.post(
            '/api/register/',
            {
                'username': 'jwttest',
                'password': 'pass123',
                'nickname': 'JWT测试'
            },
            format='json'
        )

        response = self.client.patch(
            '/api/login/',
            {
                'username': 'jwttest',
                'password': 'pass123'
            },
            format='json'
        )

        jwt_token = response.data['jwt']

        # 解码JWT
        payload = verify_jwt(jwt_token)
        self.assertIsNotNone(payload)
        self.assertIn('user_id', payload)
        self.assertIn('nickname', payload)


class UserInfoTest(APITestCase):
    """用户信息接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_get_current_user_info(self):
        """测试获取当前用户信息"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/user/info/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_user_info_by_id(self):
        """测试根据ID获取用户信息"""
        # 创建login.User
        custom_user = CustomUser.objects.create(
            username='customuser',
            password=encrypt_password('pass'),
            nickname='自定义用户'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/user/{custom_user.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], '自定义用户')

