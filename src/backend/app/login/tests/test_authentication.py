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
        # 1. 注册用户（用户名需5-12位，以字母开头且包含数字；密码需8-15位，包含大小写/数字/特殊字符）
        register_data = {
            'username': 'user123',
            'password': 'Pass123-',
            'nickname': '新用户'
        }
        response = self.client.post(
            '/api/v1/register',
            register_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. 使用注册的凭证登录
        login_data = {
            'username': 'user123',
            'password': 'Pass123-'
        }
        response = self.client.patch(
            '/api/v1/login',
            login_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data)

        jwt_token = response.data['jwt']

        # 3. 使用JWT访问受保护资源
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_token}')
        response = self.client.get('/api/v1/user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user123')

    def test_invalid_login_credentials(self):
        """测试错误凭证登录"""
        # 先注册用户（使用符合要求的用户名和密码）
        CustomUser.objects.create(
            username='user123',
            password=encrypt_password('Pass123-'),
            nickname='测试'
        )

        # 使用错误密码登录
        response = self.client.patch(
            '/api/v1/login',
            {
                'username': 'user123',
                'password': 'Wrong123-'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """测试登录不存在的用户"""
        response = self.client.patch(
            '/api/v1/login',
            {
                'username': 'nonexistent',
                'password': 'anypass'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_duplicate_username(self):
        """测试注册重复用户名"""
        # 第一次注册（使用符合要求的用户名和密码）
        self.client.post(
            '/api/v1/register',
            {
                'username': 'user123',
                'password': 'Pass123-',
                'nickname': '用户1'
            },
            format='json'
        )

        # 尝试用相同用户名注册
        response = self.client.post(
            '/api/v1/register',
            {
                'username': 'user123',
                'password': 'Pass456-',
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
            '/api/v1/register',
            {
                'username': 'user123',
                'nickname': '新用户'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """测试登出"""
        # 先注册并登录获取JWT
        self.client.post(
            '/api/v1/register',
            {
                'username': 'user123',
                'password': 'Pass123-',
                'nickname': '测试用户'
            },
            format='json'
        )

        response = self.client.patch(
            '/api/v1/login',
            {
                'username': 'user123',
                'password': 'Pass123-'
            },
            format='json'
        )

        jwt_token = response.data['jwt']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_token}')

        # 登出
        response = self.client.post('/api/v1/logout')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_resource_without_auth(self):
        """测试未认证访问受保护资源"""
        response = self.client.get('/api/v1/user')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_contains_user_info(self):
        """测试JWT包含用户信息"""
        # 注册并登录
        self.client.post(
            '/api/v1/register',
            {
                'username': 'jwt123',
                'password': 'Pass123-',
                'nickname': 'JWT测试'
            },
            format='json'
        )

        response = self.client.patch(
            '/api/v1/login',
            {
                'username': 'jwt123',
                'password': 'Pass123-'
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
        # 创建login.User并获取JWT
        self.custom_user = CustomUser.objects.create(
            username='user123',
            password=encrypt_password('Pass123-'),
            nickname='测试用户'
        )

        # 登录获取JWT token
        response = self.client.patch(
            '/api/v1/login',
            {
                'username': 'user123',
                'password': 'Pass123-'
            },
            format='json'
        )
        self.jwt_token = response.data['jwt']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')

    def test_get_current_user_info(self):
        """测试获取当前用户信息"""
        response = self.client.get('/api/v1/user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user123')
        self.assertEqual(response.data['nickname'], '测试用户')

    def test_get_user_info_by_id(self):
        """测试根据ID获取用户信息"""
        # 创建另一个用户
        custom_user2 = CustomUser.objects.create(
            username='customuser',
            password=encrypt_password('pass'),
            nickname='自定义用户'
        )

        response = self.client.get(f'/api/v1/user/{custom_user2.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], '自定义用户')

    def test_get_user_info_by_nonexistent_id(self):
        """测试获取不存在的用户信息"""
        response = self.client.get('/api/v1/user/99999')

        # 实际实现：get_user 返回 ("not found", False) 时，视图返回 500
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_register_missing_username(self):
        """测试注册缺少用户名"""
        response = self.client.post(
            '/api/v1/register',
            {
                'password': 'Pass123-',
                'nickname': '新用户'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_nickname(self):
        """测试注册缺少昵称"""
        response = self.client.post(
            '/api/v1/register',
            {
                'username': 'user123',
                'password': 'Pass123-'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_username_format(self):
        """测试注册用户名格式不符合要求（需5-12位，以字母开头且包含数字）"""
        response = self.client.post(
            '/api/v1/register',
            {
                'username': 'user',  # 太短
                'password': 'Pass123-',
                'nickname': '新用户'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_password_format(self):
        """测试注册密码格式不符合要求（需8-15位，包含大小写/数字/特殊字符）"""
        response = self.client.post(
            '/api/v1/register',
            {
                'username': 'user123',
                'password': 'pass',  # 不符合要求
                'nickname': '新用户'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_credentials(self):
        """测试空凭证登录"""
        response = self.client.patch(
            '/api/v1/login',
            {
                'username': '',
                'password': ''
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_info_with_invalid_jwt(self):
        """测试使用无效JWT获取用户信息"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_xyz')

        response = self.client.get('/api/v1/user')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_auth(self):
        """测试未登录登出"""
        self.client.credentials()  # 清除认证信息

        response = self.client.post('/api/v1/logout')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

