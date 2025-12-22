"""
测试 canteen/controllers.py 模块
"""
import unittest
from unittest.mock import patch, Mock, MagicMock
from django.test import TestCase
from decimal import Decimal

from canteen.controllers import (
    get_user_consumption,
    bind_idserial_and_fetch,
    refresh_consumption_data,
    unbind_consumption
)
from canteen.models import CanteenConsumption
from login.models import User
from utils.jwt import encrypt_password


class TestGetUserConsumption(TestCase):
    """测试获取用户消费记录函数"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create(
            username='testuser',
            password=encrypt_password('testpass123'),
            nickname='Test User'
        )

    def test_get_user_consumption_exists(self):
        """测试获取已存在的消费记录"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='test_cookie',
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        result = get_user_consumption(self.user)

        self.assertIsNotNone(result)
        self.assertEqual(result.idserial, '2023000001')
        self.assertEqual(result.user, self.user)

    def test_get_user_consumption_not_exists(self):
        """测试获取不存在的消费记录"""
        result = get_user_consumption(self.user)

        self.assertIsNone(result)


class TestBindIdserialAndFetch(TestCase):
    """测试绑定学号并获取消费数据函数"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create(
            username='testuser',
            password=encrypt_password('testpass123'),
            nickname='Test User'
        )

    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_bind_idserial_and_fetch_success_new(self, mock_fetch):
        """测试成功绑定新学号"""
        mock_fetch.return_value = {
            "success": True,
            "data": {
                "idserial": "2023000001",
                "total_amount": 100.0,
                "canteen_count": 3,
                "canteens": {"紫荆园": 50.0, "桃李园": 30.0, "丁香园": 20.0}
            },
            "servicehall": "test_cookie",
            "idserial": "2023000001",
            "error": None
        }

        success, message, data = bind_idserial_and_fetch(
            self.user,
            idserial='2023000001'
        )

        self.assertTrue(success)
        self.assertIn("绑定", message)
        self.assertIsNotNone(data)
        self.assertEqual(data["idserial"], "2023000001")

        # 验证数据库记录
        consumption = CanteenConsumption.objects.get(user=self.user)
        self.assertEqual(consumption.idserial, "2023000001")
        self.assertEqual(consumption.servicehall_cookie, "test_cookie")

    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_bind_idserial_and_fetch_success_update(self, mock_fetch):
        """测试成功更新已存在的学号"""
        # 先创建一条记录
        CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='old_cookie',
            total_amount=Decimal('50.00'),
            canteen_count=2
        )

        mock_fetch.return_value = {
            "success": True,
            "data": {
                "idserial": "2023000001",
                "total_amount": 200.0,
                "canteen_count": 5,
                "canteens": {"紫荆园": 100.0, "桃李园": 50.0, "丁香园": 30.0, "清芬园": 15.0, "听涛园": 5.0}
            },
            "servicehall": "new_cookie",
            "idserial": "2023000001",
            "error": None
        }

        success, message, data = bind_idserial_and_fetch(
            self.user,
            idserial='2023000001'
        )

        self.assertTrue(success)
        self.assertIn("更新", message)

        # 验证数据库记录已更新
        consumption = CanteenConsumption.objects.get(user=self.user)
        self.assertEqual(consumption.total_amount, Decimal('200.00'))
        self.assertEqual(consumption.canteen_count, 5)
        self.assertEqual(consumption.servicehall_cookie, "new_cookie")

    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_bind_idserial_and_fetch_failure(self, mock_fetch):
        """测试绑定失败"""
        mock_fetch.return_value = {
            "success": False,
            "data": None,
            "servicehall": None,
            "idserial": None,
            "error": "获取数据失败"
        }

        success, message, data = bind_idserial_and_fetch(
            self.user,
            idserial='2023000001'
        )

        self.assertFalse(success)
        self.assertIn("获取数据失败", message)
        self.assertIsNone(data)

        # 验证数据库中没有记录
        self.assertFalse(CanteenConsumption.objects.filter(user=self.user).exists())

    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_bind_idserial_and_fetch_exception(self, mock_fetch):
        """测试绑定过程中发生异常"""
        mock_fetch.side_effect = Exception("网络错误")

        success, message, data = bind_idserial_and_fetch(
            self.user,
            idserial='2023000001'
        )

        self.assertFalse(success)
        self.assertIn("操作失败", message)
        self.assertIsNone(data)


class TestRefreshConsumptionData(TestCase):
    """测试刷新消费数据函数"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create(
            username='testuser',
            password=encrypt_password('testpass123'),
            nickname='Test User'
        )

    def test_refresh_consumption_data_not_bound(self):
        """测试未绑定学号时刷新"""
        success, message, data = refresh_consumption_data(self.user)

        self.assertFalse(success)
        self.assertIn("请先绑定学号", message)
        self.assertIsNone(data)

    @patch('canteen.controllers.fetch_canteen_data')
    def test_refresh_consumption_data_with_servicehall_success(self, mock_fetch):
        """测试使用提供的servicehall成功刷新"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='old_cookie',
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        mock_fetch.return_value = {
            "success": True,
            "data": {
                "idserial": "2023000001",
                "total_amount": 200.0,
                "canteen_count": 5,
                "canteens": {"紫荆园": 100.0, "桃李园": 50.0}
            },
            "error": None
        }

        success, message, data = refresh_consumption_data(
            self.user,
            servicehall='new_cookie'
        )

        self.assertTrue(success)
        self.assertIn("刷新成功", message)
        self.assertIsNotNone(data)

        # 验证数据库记录已更新
        consumption.refresh_from_db()
        self.assertEqual(consumption.total_amount, Decimal('200.00'))
        self.assertEqual(consumption.canteen_count, 5)
        self.assertEqual(consumption.servicehall_cookie, "new_cookie")

    @patch('canteen.controllers.fetch_canteen_data')
    def test_refresh_consumption_data_with_saved_cookie_success(self, mock_fetch):
        """测试使用保存的cookie成功刷新"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='saved_cookie',
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        mock_fetch.return_value = {
            "success": True,
            "data": {
                "idserial": "2023000001",
                "total_amount": 150.0,
                "canteen_count": 4,
                "canteens": {"紫荆园": 80.0, "桃李园": 40.0, "丁香园": 20.0, "清芬园": 10.0}
            },
            "error": None
        }

        success, message, data = refresh_consumption_data(self.user)

        self.assertTrue(success)
        # 验证使用了保存的cookie
        mock_fetch.assert_called_once_with('2023000001', 'saved_cookie')

    @patch('canteen.controllers.fetch_canteen_data')
    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_refresh_consumption_data_cookie_expired(self, mock_fetch_and_parse, mock_fetch):
        """测试cookie失效后重新获取"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='expired_cookie',
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        # 第一次调用返回失败（cookie失效）
        mock_fetch.return_value = {
            "success": False,
            "data": None,
            "error": "Cookie失效"
        }

        # 重新获取cookie和数据
        mock_fetch_and_parse.return_value = {
            "success": True,
            "data": {
                "idserial": "2023000001",
                "total_amount": 180.0,
                "canteen_count": 4,
                "canteens": {"紫荆园": 90.0, "桃李园": 50.0}
            },
            "servicehall": "new_cookie",
            "idserial": "2023000001",
            "error": None
        }

        success, message, data = refresh_consumption_data(self.user)

        self.assertTrue(success)
        # 验证调用了重新获取
        mock_fetch_and_parse.assert_called_once()

    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_refresh_consumption_data_no_cookie(self, mock_fetch_and_parse):
        """测试没有cookie时重新获取"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie=None,  # 没有cookie
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        mock_fetch_and_parse.return_value = {
            "success": True,
            "data": {
                "idserial": "2023000001",
                "total_amount": 200.0,
                "canteen_count": 5,
                "canteens": {"紫荆园": 100.0}
            },
            "servicehall": "new_cookie",
            "idserial": "2023000001",
            "error": None
        }

        success, message, data = refresh_consumption_data(self.user)

        self.assertTrue(success)
        mock_fetch_and_parse.assert_called_once()

    @patch('canteen.controllers.fetch_canteen_data')
    @patch('canteen.controllers.fetch_and_parse_consumption')
    def test_refresh_consumption_data_fetch_failure(self, mock_fetch_and_parse, mock_fetch):
        """测试获取数据失败"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='test_cookie',
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        mock_fetch.return_value = {
            "success": False,
            "data": None,
            "error": "网络错误"
        }
        # 当fetch_canteen_data失败时，会尝试fetch_and_parse_consumption，也让它失败
        mock_fetch_and_parse.return_value = {
            "success": False,
            "data": None,
            "error": "网络错误"
        }

        success, message, data = refresh_consumption_data(
            self.user,
            servicehall='test_cookie'
        )

        self.assertFalse(success)
        self.assertIn("网络错误", message)
        self.assertIsNone(data)

    @patch('canteen.controllers.fetch_canteen_data')
    def test_refresh_consumption_data_exception(self, mock_fetch):
        """测试刷新过程中发生异常"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='test_cookie',
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        mock_fetch.side_effect = Exception("数据库错误")

        success, message, data = refresh_consumption_data(
            self.user,
            servicehall='test_cookie'
        )

        self.assertFalse(success)
        self.assertIn("刷新失败", message)
        self.assertIsNone(data)


class TestUnbindConsumption(TestCase):
    """测试解绑消费记录函数"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create(
            username='testuser',
            password=encrypt_password('testpass123'),
            nickname='Test User'
        )

    def test_unbind_consumption_success(self):
        """测试成功解绑"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='test_cookie',
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        success, message = unbind_consumption(self.user)

        self.assertTrue(success)
        self.assertIn("解绑成功", message)
        # 验证记录已删除
        self.assertFalse(CanteenConsumption.objects.filter(user=self.user).exists())

    def test_unbind_consumption_not_bound(self):
        """测试未绑定时解绑"""
        success, message = unbind_consumption(self.user)

        self.assertFalse(success)
        self.assertIn("未绑定学号", message)

    def test_unbind_consumption_exception(self):
        """测试解绑过程中发生异常"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='test_cookie',
            total_amount=Decimal('100.00'),
            canteen_count=3
        )

        # 模拟删除时发生异常
        with patch.object(CanteenConsumption, 'delete', side_effect=Exception("数据库错误")):
            success, message = unbind_consumption(self.user)

            self.assertFalse(success)
            self.assertIn("解绑失败", message)

