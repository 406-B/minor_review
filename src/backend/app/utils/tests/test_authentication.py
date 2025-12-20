"""
单元测试：认证工具函数
测试登录验证装饰器等功能
"""
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status

from utils.jwt import generate_jwt, verify_jwt
from login.models import User as CustomUser
from utils.authentication import JWTAuthentication


class LoginRequiredDecoratorTest(TestCase):
    """登录验证装饰器测试"""

    def setUp(self):
        self.factory = RequestFactory()
        # 使用 login.models.User
        self.user = CustomUser.objects.create(
            username='testuser',
            password='encrypted_password',
            nickname='测试用户'
        )
        self.user.is_staff = False
        self.user.is_superuser = False
        self.user.is_active = True

    def test_login_required_with_valid_token(self):
        """测试有效token访问受保护视图"""
        # 生成JWT（使用正确的用户ID）
        payload = {'user_id': self.user.id, 'nickname': 'testuser'}
        token = generate_jwt(payload)

        # 创建带Authorization header的请求
        request = self.factory.get('/api/protected/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        # 使用JWTAuthentication进行认证
        auth = JWTAuthentication()
        result = auth.authenticate(request)

        # 应该成功认证
        self.assertIsNotNone(result)
        if result:
            user, payload = result
            self.assertEqual(user.id, self.user.id)

    def test_login_required_without_token(self):
        """测试无token访问受保护视图"""
        request = self.factory.get('/api/protected/')

        # 使用JWTAuthentication进行认证
        auth = JWTAuthentication()
        result = auth.authenticate(request)

        # 应该返回None（未认证）
        self.assertIsNone(result)

    def test_login_required_with_invalid_token(self):
        """测试无效token访问受保护视图"""
        request = self.factory.get('/api/protected/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token_xyz'

        # 使用JWTAuthentication进行认证
        auth = JWTAuthentication()
        result = auth.authenticate(request)

        # 应该返回None（无效token）
        self.assertIsNone(result)

    def test_login_required_with_malformed_header(self):
        """测试格式错误的Authorization header"""
        request = self.factory.get('/api/protected/')
        auth = JWTAuthentication()

        # 测试各种格式错误
        malformed_headers = [
            'InvalidFormat token',
            'Bearer',  # 缺少token
            'token_without_bearer',
            '',
        ]

        for header in malformed_headers:
            request.META['HTTP_AUTHORIZATION'] = header
            result = auth.authenticate(request)
            # 格式错误的header应该返回None
            self.assertIsNone(result)

