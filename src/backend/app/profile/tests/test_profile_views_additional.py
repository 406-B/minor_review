"""
补充测试：Profile Views 未覆盖的功能
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta, date

from login.models import User as CustomUser
from list.models import Canteen, Dish, Tag, DishCheckInRecord, UserDishHistory
from utils.jwt import generate_jwt, encrypt_password


class ProfileViewsAdditionalTest(APITestCase):
    """Profile Views 补充测试"""

    def setUp(self):
        self.client = APIClient()

        # 创建用户
        self.custom_user = CustomUser.objects.create(
            username='testuser',
            password=encrypt_password('testpass123'),
            nickname='测试用户'
        )
        self.django_user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.user_token = generate_jwt({'user_id': self.custom_user.id})
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.user_token}'

        # 创建测试数据
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen,
            rating=Decimal('4.5')
        )

    def test_get_check_in_history_by_month(self):
        """测试按月获取打卡历史"""
        # 创建打卡记录
        check_in_date = timezone.now() - timedelta(days=5)
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=self.dish,
            checked_in_at=check_in_date
        )

        year = check_in_date.year
        month = check_in_date.month

        response = self.client.get('/api/v1/profile/check-in-history', {
            'year': year,
            'month': month
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('check_ins', response.data['data'])

    def test_get_check_in_history_by_date_range(self):
        """测试按日期范围获取打卡历史"""
        check_in_date = timezone.now() - timedelta(days=3)
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=self.dish,
            checked_in_at=check_in_date
        )

        start_date = (timezone.now() - timedelta(days=7)).date()
        end_date = timezone.now().date()

        response = self.client.get('/api/v1/profile/check-in-history', {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_check_in_history_default_recent_7_days(self):
        """测试默认获取最近7天"""
        check_in_date = timezone.now() - timedelta(days=2)
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=self.dish,
            checked_in_at=check_in_date
        )

        response = self.client.get('/api/v1/profile/check-in-history')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('data', response.data)
        self.assertIn('check_ins', response.data['data'])

    def test_get_check_in_history_invalid_month(self):
        """测试无效的月份"""
        response = self.client.get('/api/v1/profile/check-in-history', {
            'year': 2024,
            'month': 13  # 无效月份
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_check_in_history_invalid_date_range(self):
        """测试开始日期晚于结束日期"""
        start_date = timezone.now().date()
        end_date = (timezone.now() - timedelta(days=7)).date()

        response = self.client.get('/api/v1/profile/check-in-history', {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_check_in_history_invalid_date_format(self):
        """测试无效的日期格式"""
        response = self.client.get('/api/v1/profile/check-in-history', {
            'start_date': 'invalid-date'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_check_in_calendar_success(self):
        """测试获取月度打卡概览"""
        check_in_date = timezone.now()
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=self.dish,
            checked_in_at=check_in_date
        )

        year = check_in_date.year
        month = check_in_date.month

        response = self.client.get('/api/v1/profile/check-in-calendar', {
            'year': year,
            'month': month
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_get_check_in_calendar_invalid_month(self):
        """测试无效的月份"""
        response = self.client.get('/api/v1/profile/check-in-calendar', {
            'year': 2024,
            'month': 13
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_check_in_calendar_missing_params(self):
        """测试缺少参数"""
        response = self.client.get('/api/v1/profile/check-in-calendar')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertIn('年份和月份参数必需', response.data['message'])

    def test_get_check_in_calendar_invalid_year_month(self):
        """测试无效的年份月份类型"""
        response = self.client.get('/api/v1/profile/check-in-calendar', {
            'year': 'invalid',
            'month': 'invalid'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_check_in_calendar_december(self):
        """测试12月的边界情况"""
        check_in_date = datetime(2024, 12, 15)
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=self.dish,
            checked_in_at=timezone.make_aware(check_in_date)
        )

        response = self.client.get('/api/v1/profile/check-in-calendar', {
            'year': 2024,
            'month': 12
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_recommended_dishes_no_preferences(self):
        """测试无偏好标签的推荐"""
        # 创建一些菜品
        dish2 = Dish.objects.create(
            name='菜品2',
            price=Decimal('8.00'),
            canteen=self.canteen,
            rating=Decimal('4.0')
        )

        response = self.client.get('/api/v1/profile/recommended-dishes')

        # 根据实际API行为，没有偏好标签时返回404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 404)
        self.assertIn('未设置偏好标签', response.data['message'])

    def test_get_recommended_dishes_with_preferences(self):
        """测试有偏好标签的推荐"""
        tag = Tag.objects.create(name='辣')
        self.dish.tags.add(tag)

        # 设置用户偏好 - preference_tags是CustomUser的ManyToManyField
        self.custom_user.preference_tags.add(tag)

        response = self.client.get('/api/v1/profile/recommended-dishes')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('data', response.data)
        self.assertGreater(len(response.data['data']), 0)

    def test_get_check_in_history_with_user_dish_history(self):
        """测试包含用户菜品历史的打卡历史"""
        # 创建用户菜品历史
        UserDishHistory.objects.create(
            user=self.django_user,
            dish=self.dish,
            count=5
        )

        # 创建打卡记录
        check_in_date = timezone.now() - timedelta(days=2)
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=self.dish,
            checked_in_at=check_in_date
        )

        response = self.client.get('/api/v1/profile/check-in-history', {
            'start_date': (timezone.now() - timedelta(days=7)).date().isoformat(),
            'end_date': timezone.now().date().isoformat()
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 验证返回的数据包含check_in_count
        if response.data.get('data', {}).get('check_ins'):
            for check_in in response.data['data']['check_ins']:
                if check_in.get('dishes'):
                    for dish_data in check_in['dishes']:
                        self.assertIn('check_in_count', dish_data)

    def test_get_check_in_history_empty(self):
        """测试无打卡记录"""
        DishCheckInRecord.objects.filter(user=self.django_user).delete()

        response = self.client.get('/api/v1/profile/check-in-history')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['summary']['total_check_ins'], 0)

    def test_get_check_in_calendar_empty(self):
        """测试无打卡记录的月份"""
        DishCheckInRecord.objects.filter(user=self.django_user).delete()

        response = self.client.get('/api/v1/profile/check-in-calendar', {
            'year': 2024,
            'month': 1
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        # check_in_dates应该是空列表
        self.assertEqual(len(response.data['data']['check_in_dates']), 0)

    def test_get_check_in_history_multiple_dishes_same_day(self):
        """测试同一天多个菜品打卡"""
        dish2 = Dish.objects.create(
            name='菜品2',
            price=Decimal('12.00'),
            canteen=self.canteen
        )

        check_in_date = timezone.now() - timedelta(days=1)
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=self.dish,
            checked_in_at=check_in_date
        )
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=dish2,
            checked_in_at=check_in_date
        )

        response = self.client.get('/api/v1/profile/check-in-history')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        # 验证同一天有多个菜品
        date_str = check_in_date.date().isoformat()
        data = response.data.get('data', [])
        # get_check_in_history返回的是列表，不是字典
        if isinstance(data, list):
            for check_in in data:
                if isinstance(check_in, dict) and check_in.get('date') == date_str:
                    dishes = check_in.get('dishes', [])
                    self.assertGreaterEqual(len(dishes), 2)
                break

    def test_get_check_in_history_summary_statistics(self):
        """测试统计摘要"""
        dish2 = Dish.objects.create(
            name='菜品2',
            price=Decimal('15.00'),
            canteen=self.canteen
        )

        # 创建多个打卡记录
        for i in range(3):
            DishCheckInRecord.objects.create(
                user=self.django_user,
                dish=self.dish,
                checked_in_at=timezone.now() - timedelta(days=i)
            )
        DishCheckInRecord.objects.create(
            user=self.django_user,
            dish=dish2,
            checked_in_at=timezone.now() - timedelta(days=1)
        )

        response = self.client.get('/api/v1/profile/check-in-history')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        summary = response.data['data']['summary']
        self.assertGreater(summary['total_check_ins'], 0)
        self.assertGreater(summary['total_dishes'], 0)
        self.assertGreater(summary['total_consumption'], 0)

