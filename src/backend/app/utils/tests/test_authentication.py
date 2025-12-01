"""
单元测试：认证工具函数
测试登录验证装饰器等功能
"""
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from django.contrib.auth.models import User

from utils.jwt import generate_jwt, login_required
from login.models import User as CustomUser


class LoginRequiredDecoratorTest(TestCase):
    """登录验证装饰器测试"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # 创建一个简单的被装饰视图
        @login_required
        def protected_view(request):
            return JsonResponse({'message': 'success', 'user': request.user.username})

        self.protected_view = protected_view

    def test_login_required_with_valid_token(self):
        """测试有效token访问受保护视图"""
        # 生成JWT
        payload = {'user_id': self.user.id, 'nickname': 'testuser'}
        token = generate_jwt(payload)

        # 创建带Authorization header的请求
        request = self.factory.get('/api/protected/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        response = self.protected_view(request)

        # 应该成功返回
        self.assertEqual(response.status_code, 200)

    def test_login_required_without_token(self):
        """测试无token访问受保护视图"""
        request = self.factory.get('/api/protected/')

        response = self.protected_view(request)

        # 应该返回401
        self.assertEqual(response.status_code, 401)

    def test_login_required_with_invalid_token(self):
        """测试无效token访问受保护视图"""
        request = self.factory.get('/api/protected/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token_xyz'

        response = self.protected_view(request)

        # 应该返回401
        self.assertEqual(response.status_code, 401)

    def test_login_required_with_malformed_header(self):
        """测试格式错误的Authorization header"""
        request = self.factory.get('/api/protected/')

        # 测试各种格式错误
        malformed_headers = [
            'InvalidFormat token',
            'Bearer',  # 缺少token
            'token_without_bearer',
            '',
        ]

        for header in malformed_headers:
            request.META['HTTP_AUTHORIZATION'] = header
            response = self.protected_view(request)
            self.assertEqual(response.status_code, 401)

