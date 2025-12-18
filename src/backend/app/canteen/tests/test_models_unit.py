"""
单元测试：Canteen App Models
测试食堂消费数据模型
"""
from django.test import TestCase
from decimal import Decimal
from django.contrib.auth.models import User

from canteen.models import CanteenConsumption


class CanteenConsumptionModelTest(TestCase):
    """食堂消费记录模型单元测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_canteen_consumption_creation(self):
        """测试食堂消费记录创建"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            servicehall_cookie='test_cookie_123',
            total_amount=Decimal('150.50'),
            canteen_count=3,
            canteen_data={
                '清华园食堂': Decimal('80.00'),
                '紫荆园食堂': Decimal('45.50'),
                '桃李园食堂': Decimal('25.00')
            }
        )

        self.assertEqual(consumption.user, self.user)
        self.assertEqual(consumption.idserial, '2023000001')
        self.assertEqual(consumption.servicehall_cookie, 'test_cookie_123')
        self.assertEqual(consumption.total_amount, Decimal('150.50'))
        self.assertEqual(consumption.canteen_count, 3)
        self.assertEqual(len(consumption.canteen_data), 3)
        self.assertIsNotNone(consumption.created)
        self.assertIsNotNone(consumption.last_fetched)

    def test_canteen_consumption_str_method(self):
        """测试食堂消费记录字符串表示"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            total_amount=Decimal('100.00')
        )

        expected_str = f'{self.user.username} - 2023000001 - ¥100.00'
        self.assertEqual(str(consumption), expected_str)

    def test_canteen_consumption_default_values(self):
        """测试食堂消费记录默认值"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001'
        )

        self.assertEqual(consumption.total_amount, Decimal('0'))
        self.assertEqual(consumption.canteen_count, 0)
        self.assertEqual(consumption.canteen_data, {})
        self.assertIsNone(consumption.servicehall_cookie)

    def test_canteen_consumption_update_last_fetched(self):
        """测试更新最后获取时间"""
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001'
        )

        original_time = consumption.last_fetched
        consumption.save()  # 应该自动更新last_fetched

        consumption.refresh_from_db()
        self.assertGreaterEqual(consumption.last_fetched, original_time)

    def test_canteen_consumption_unique_user(self):
        """测试用户唯一性约束"""
        CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001'
        )

        # 同一个用户不能创建多个消费记录
        with self.assertRaises(Exception):  # 应该抛出完整性错误
            CanteenConsumption.objects.create(
                user=self.user,
                idserial='2023000002'
            )

    def test_canteen_consumption_json_field_handling(self):
        """测试JSON字段的处理"""
        # 测试空字典
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            canteen_data={}
        )

        self.assertEqual(consumption.canteen_data, {})

        # 测试包含Decimal的字典
        canteen_data = {
            '食堂A': Decimal('10.50'),
            '食堂B': Decimal('20.75')
        }
        consumption.canteen_data = canteen_data
        consumption.save()

        consumption.refresh_from_db()
        self.assertEqual(consumption.canteen_data, canteen_data)

    def test_canteen_consumption_ordering(self):
        """测试默认排序（按最后更新时间倒序）"""
        from django.utils import timezone
        import time

        consumption1 = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001'
        )

        # 等待一小段时间确保时间戳不同
        time.sleep(0.01)

        user2 = User.objects.create_user(
            username='user2',
            password='pass2'
        )
        consumption2 = CanteenConsumption.objects.create(
            user=user2,
            idserial='2023000002'
        )

        # 查询时应该按last_fetched倒序排列
        consumptions = CanteenConsumption.objects.all()
        self.assertEqual(consumptions[0], consumption2)  # 后创建的排在前面
        self.assertEqual(consumptions[1], consumption1)

    def test_canteen_consumption_data_validation(self):
        """测试数据有效性"""
        # 测试负数金额（如果模型允许的话）
        consumption = CanteenConsumption.objects.create(
            user=self.user,
            idserial='2023000001',
            total_amount=Decimal('-10.00')
        )

        self.assertEqual(consumption.total_amount, Decimal('-10.00'))

        # 测试负数食堂数量
        consumption.canteen_count = -1
        consumption.save()
        consumption.refresh_from_db()
        self.assertEqual(consumption.canteen_count, -1)

    def test_canteen_consumption_bulk_operations(self):
        """测试批量操作"""
        users_data = [
            {'username': f'user{i}', 'idserial': f'202300000{i}'}
            for i in range(1, 6)
        ]

        # 批量创建用户和消费记录
        consumptions = []
        for data in users_data:
            user = User.objects.create_user(
                username=data['username'],
                password='testpass'
            )
            consumption = CanteenConsumption.objects.create(
                user=user,
                idserial=data['idserial'],
                total_amount=Decimal('50.00')
            )
            consumptions.append(consumption)

        # 验证批量创建结果
        self.assertEqual(CanteenConsumption.objects.count(), 5)
        self.assertEqual(User.objects.count(), 6)  # 包括setup中创建的用户

        # 测试批量更新
        CanteenConsumption.objects.filter(
            total_amount=Decimal('50.00')
        ).update(total_amount=Decimal('75.00'))

        updated_count = CanteenConsumption.objects.filter(
            total_amount=Decimal('75.00')
        ).count()
        self.assertEqual(updated_count, 5)
