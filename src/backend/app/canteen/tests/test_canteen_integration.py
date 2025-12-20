"""
集成测试：Canteen App Views
测试食堂消费数据API端点的完整请求-响应流程
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock

from canteen.models import CanteenConsumption
from login.models import User as CustomUser
from utils.jwt import generate_jwt


class CanteenViewsIntegrationTest(APITestCase):
    """食堂相关视图集成测试"""

    def setUp(self):
        self.client = APIClient()

        # 创建测试用户 - 使用自定义User模型
        from login.models import User as CustomUser
        from utils.jwt import encrypt_password

        self.custom_user = CustomUser.objects.create(
            username='testuser',
            password=encrypt_password('testpass123'),
            nickname='测试用户'
        )
        self.custom_user.is_staff = False
        self.custom_user.is_superuser = False
        self.custom_user.is_active = True

        # 为兼容性创建Django Auth User
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass'
        )

        # 生成JWT token用于认证（使用CustomUser的id）
        self.user_token = generate_jwt({'user_id': self.custom_user.id})

    def authenticate_as_user(self):
        """设置用户认证头"""
        self.client.defaults['HTTP_AUTHORIZATION'] = self.user_token

    def authenticate_as_admin(self):
        """设置管理员认证头"""
        self.client.defaults['HTTP_AUTHORIZATION'] = self.admin_token

    def test_get_consumption_no_data(self):
        """测试获取消费数据 - 未绑定情况"""
        self.authenticate_as_user()

        response = self.client.get('/api/v1/canteen/consumption/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 404)
        self.assertIn('未绑定', response.data['message'])

    def test_get_consumption_success(self):
        """测试成功获取消费数据"""
        self.authenticate_as_user()

        # 创建消费记录
        consumption = CanteenConsumption.objects.create(
            user=self.custom_user,
            idserial='2023000001',
            total_amount=Decimal('150.50'),
            canteen_count=3,
            canteen_data={
                '清华园食堂': 80.00,
                '紫荆园食堂': 45.50,
                '桃李园食堂': 25.00
            }
        )

        response = self.client.get('/api/v1/canteen/consumption/')

        # Mock生效，期望200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['idserial'], '2023000001')
        self.assertEqual(float(response.data['data']['total_amount']), 150.5)
        self.assertEqual(response.data['data']['canteen_count'], 3)
        self.assertEqual(len(response.data['data']['canteen_data']), 3)

    def test_get_consumption_unauthorized(self):
        """测试未登录获取消费数据"""
        response = self.client.get('/api/v1/canteen/consumption/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('canteen.views.bind_idserial_and_fetch')
    def test_bind_idserial_success(self, mock_bind):
        """测试成功绑定学号"""
        self.authenticate_as_user()

        # Mock绑定函数返回成功
        mock_bind.return_value = (True, "绑定成功", {
            'idserial': '2023000001',
            'total_amount': Decimal('100.00'),
            'canteen_count': 2
        })

        data = {
            'idserial': '2023000001',
            'browser_type': 'chrome'
        }

        response = self.client.post(
            '/api/v1/canteen/bind/',
            data,
            format='json'
        )

        # Mock生效，期望200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('canteen.views.bind_idserial_and_fetch')
    def test_bind_idserial_without_idserial(self, mock_bind):
        """测试绑定学号时不提供idserial"""
        self.authenticate_as_user()

        # Mock绑定函数返回成功
        mock_bind.return_value = (True, "绑定成功", {
            'idserial': '2023000001',  # 系统自动提取
            'total_amount': Decimal('100.00')
        })

        data = {
            'browser_type': 'firefox'
        }

        response = self.client.post(
            '/api/v1/canteen/bind/',
            data,
            format='json'
        )

        # Mock生效，期望200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证mock函数被调用
        self.assertTrue(mock_bind.called)

    @patch('canteen.controllers.bind_idserial_and_fetch')
    def test_bind_idserial_failure(self, mock_bind):
        """测试绑定学号失败"""
        self.authenticate_as_user()

        # Mock绑定函数返回失败
        mock_bind.return_value = (False, "绑定失败：网络错误", None)

        data = {
            'idserial': '2023000001'
        }

        response = self.client.post(
            '/api/v1/canteen/bind/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['code'], 500)
        self.assertIn('绑定失败', response.data['message'])

    def test_bind_idserial_invalid_data(self):
        """测试绑定学号时提供无效数据"""
        self.authenticate_as_user()

        # 由于serializer中所有字段都是可选的，空数据会尝试绑定
        response = self.client.post(
            '/api/v1/canteen/bind/',
            {},
            format='json'
        )

        # 空数据时会尝试绑定，可能返回500（因为没有mock）或200（如果API处理了）
        # 这里我们期望500，因为没有提供必要的数据
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_bind_idserial_unauthorized(self):
        """测试未登录绑定学号"""
        data = {
            'idserial': '2023000001'
        }

        response = self.client.post(
            '/api/v1/canteen/bind/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('canteen.views.refresh_consumption_data')
    def test_refresh_consumption_success(self, mock_refresh):
        """测试成功刷新消费数据"""
        self.authenticate_as_user()

        # 先创建消费记录
        CanteenConsumption.objects.create(
            user=self.custom_user,
            idserial='2023000001',
            servicehall_cookie='old_cookie'
        )

        # Mock刷新函数返回成功
        mock_refresh.return_value = (True, "刷新成功", {
            'total_amount': Decimal('200.00'),
            'canteen_count': 3
        })

        data = {
            'browser_type': 'chrome'
        }

        response = self.client.post(
            '/api/v1/canteen/refresh/',
            data,
            format='json'
        )

        # Mock生效，期望200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('刷新成功', response.data['message'])

        # 验证mock函数被调用
        self.assertTrue(mock_refresh.called)

    @patch('canteen.views.refresh_consumption_data')
    def test_refresh_consumption_with_cookie(self, mock_refresh):
        """测试使用已有cookie刷新消费数据"""
        self.authenticate_as_user()

        # 创建带cookie的消费记录
        CanteenConsumption.objects.create(
            user=self.custom_user,
            idserial='2023000001',
            servicehall_cookie='saved_cookie_123'
        )

        mock_refresh.return_value = (True, "刷新成功", {})

        data = {
            'servicehall': 'saved_cookie_123'
        }

        response = self.client.post(
            '/api/v1/canteen/refresh/',
            data,
            format='json'
        )

        # Mock生效，期望200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证mock函数被调用
        self.assertTrue(mock_refresh.called)

    @patch('canteen.views.refresh_consumption_data')
    def test_refresh_consumption_not_bound(self, mock_refresh):
        """测试未绑定用户刷新消费数据"""
        self.authenticate_as_user()

        mock_refresh.return_value = (False, "请先绑定学号", None)

        data = {
            'browser_type': 'chrome'
        }

        response = self.client.post(
            '/api/v1/canteen/refresh/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertIn('请先绑定', response.data['message'])

    @patch('canteen.views.unbind_consumption')
    def test_unbind_consumption_success(self, mock_unbind):
        """测试成功解绑消费数据"""
        self.authenticate_as_user()

        # 创建消费记录
        CanteenConsumption.objects.create(
            user=self.custom_user,
            idserial='2023000001'
        )

        mock_unbind.return_value = (True, "解绑成功")

        response = self.client.delete('/api/v1/canteen/unbind/')

        # Mock生效，期望200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('解绑成功', response.data['message'])

        # Mock调用，不检查数据库（因为Mock不真实删除）
        self.assertTrue(mock_unbind.called)

    @patch('canteen.views.unbind_consumption')
    def test_unbind_consumption_not_bound(self, mock_unbind):
        """测试解绑未绑定的用户"""
        self.authenticate_as_user()

        mock_unbind.return_value = (False, "未绑定学号")

        response = self.client.delete('/api/v1/canteen/unbind/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertIn('未绑定', response.data['message'])

    def test_unbind_consumption_unauthorized(self):
        """测试未登录解绑消费数据"""
        response = self.client.delete('/api/v1/canteen/unbind/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
