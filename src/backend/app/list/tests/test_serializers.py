"""
单元测试：List App Serializers
测试所有序列化器的功能
"""
from django.test import TestCase
from decimal import Decimal
from datetime import datetime
from django.utils import timezone

from list.models import Canteen, Dish, Tag, Rating, Review, Floor, Window, UserDishHistory, DishCheckInRecord
from list.serializers import (
    CanteenSerializer, DishSerializer, DishListSerializer, TagSerializer,
    FloorSerializer, WindowSerializer, RatingSerializer, ReviewSerializer,
    ReviewListSerializer, UserDishHistorySerializer
)
from django.contrib.auth.models import User as AuthUser
from login.models import User as CustomUser
from utils.jwt import encrypt_password


class CanteenSerializerTest(TestCase):
    """食堂序列化器测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(
            name='测试食堂',
            address='测试地址',
            latitude=39.9042,
            longitude=116.4074
        )

    def test_canteen_serializer(self):
        """测试食堂序列化器"""
        serializer = CanteenSerializer(self.canteen)
        data = serializer.data

        self.assertEqual(data['id'], self.canteen.id)
        self.assertEqual(data['name'], '测试食堂')
        self.assertEqual(data['address'], '测试地址')
        self.assertEqual(float(data['latitude']), 39.9042)
        self.assertEqual(float(data['longitude']), 116.4074)

    def test_canteen_serializer_with_null_coordinates(self):
        """测试食堂序列化器（坐标为null）"""
        canteen = Canteen.objects.create(name='无坐标食堂')
        serializer = CanteenSerializer(canteen)
        data = serializer.data

        self.assertIsNone(data['latitude'])
        self.assertIsNone(data['longitude'])


class DishSerializerTest(TestCase):
    """菜品序列化器测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            description='测试描述',
            price=Decimal('15.50'),
            canteen=self.canteen,
            rating=Decimal('4.2'),
            view_count=100
        )
        self.tag = Tag.objects.create(name='辣')
        self.dish.tags.add(self.tag)

    def test_dish_serializer(self):
        """测试菜品序列化器"""
        serializer = DishSerializer(self.dish)
        data = serializer.data

        self.assertEqual(data['id'], self.dish.id)
        self.assertEqual(data['name'], '测试菜品')
        self.assertEqual(data['description'], '测试描述')
        self.assertEqual(float(data['price']), 15.5)
        self.assertEqual(float(data['rating']), 4.2)
        self.assertEqual(data['view_count'], 100)
        self.assertEqual(data['canteen_name'], '测试食堂')
        self.assertEqual(len(data['tags']), 1)
        self.assertEqual(data['tags'][0]['name'], '辣')


class DishListSerializerTest(TestCase):
    """菜品列表序列化器测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('15.50'),
            canteen=self.canteen,
            rating=Decimal('4.2'),
            view_count=100
        )
        self.tag = Tag.objects.create(name='辣')
        self.dish.tags.add(self.tag)

    def test_dish_list_serializer(self):
        """测试菜品列表序列化器"""
        serializer = DishListSerializer(self.dish)
        data = serializer.data

        # DishListSerializer 不包含 description
        self.assertEqual(data['id'], self.dish.id)
        self.assertEqual(data['name'], '测试菜品')
        self.assertEqual(float(data['price']), 15.5)
        self.assertEqual(float(data['rating']), 4.2)
        self.assertEqual(data['view_count'], 100)
        self.assertEqual(data['canteen_name'], '测试食堂')
        self.assertEqual(len(data['tags']), 1)
        self.assertEqual(data['tags'][0]['name'], '辣')
        self.assertNotIn('description', data)


class TagSerializerTest(TestCase):
    """标签序列化器测试"""

    def setUp(self):
        self.tag = Tag.objects.create(name='辣')

    def test_tag_serializer(self):
        """测试标签序列化器"""
        serializer = TagSerializer(self.tag)
        data = serializer.data

        self.assertEqual(data['id'], self.tag.id)
        self.assertEqual(data['name'], '辣')


class FloorWindowSerializerTest(TestCase):
    """楼层窗口序列化器测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.floor = Floor.objects.create(
            name='一层',
            canteen=self.canteen,
            order=1
        )
        self.window = Window.objects.create(
            name='川菜窗口',
            floor=self.floor,
            order=1
        )
        self.dish = Dish.objects.create(
            name='宫保鸡丁',
            price=Decimal('12.00'),
            canteen=self.canteen,
            window=self.window
        )

    def test_floor_serializer(self):
        """测试楼层序列化器"""
        serializer = FloorSerializer(self.floor)
        data = serializer.data

        self.assertEqual(data['id'], self.floor.id)
        self.assertEqual(data['name'], '一层')
        self.assertEqual(data['order'], 1)
        # FloorSerializer 不包含 canteen 字段
        self.assertIn('windows', data)
        self.assertEqual(len(data['windows']), 1)
        self.assertEqual(data['windows'][0]['name'], '川菜窗口')

    def test_window_serializer(self):
        """测试窗口序列化器"""
        # WindowSerializer 只包含 id, name, order 字段
        from list.serializers import WindowSerializer
        serializer = WindowSerializer(self.window)
        data = serializer.data

        self.assertEqual(data['id'], self.window.id)
        self.assertEqual(data['name'], '川菜窗口')
        self.assertEqual(data['order'], 1)
        # WindowSerializer 不包含 floor 字段


class RatingSerializerTest(TestCase):
    """评分序列化器测试"""

    def setUp(self):
        self.user = AuthUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )
        self.rating = Rating.objects.create(
            user=self.user,
            dish=self.dish,
            score=Decimal('4.5')
        )

    def test_rating_serializer(self):
        """测试评分序列化器"""
        serializer = RatingSerializer(self.rating)
        data = serializer.data

        self.assertEqual(data['id'], self.rating.id)
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['dish'], self.dish.id)
        self.assertEqual(float(data['score']), 4.5)


class ReviewSerializerTest(TestCase):
    """评论序列化器测试"""

    def setUp(self):
        self.user = AuthUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )
        self.review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='很好吃！',
            likes_count=5
        )

    def test_review_serializer(self):
        """测试评论序列化器"""
        serializer = ReviewSerializer(self.review)
        data = serializer.data

        self.assertEqual(data['id'], self.review.id)
        # 检查是否有用户相关字段，根据序列化器定义
        self.assertEqual(data['content'], '很好吃！')
        self.assertEqual(data['likes_count'], 5)

    def test_review_list_serializer(self):
        """测试评论列表序列化器"""
        serializer = ReviewListSerializer(self.review)
        data = serializer.data

        # ReviewListSerializer 应该有简化的字段
        self.assertEqual(data['id'], self.review.id)
        self.assertEqual(data['content'], '很好吃！')
        self.assertEqual(data['likes_count'], 5)
        # 可能包含用户基本信息
        self.assertIn('user', data)


class UserDishHistorySerializerTest(TestCase):
    """用户菜品历史序列化器测试"""

    def setUp(self):
        self.user = AuthUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )
        self.history = UserDishHistory.objects.create(
            user=self.user,
            dish=self.dish,
            count=5
        )

    def test_user_dish_history_serializer(self):
        """测试用户菜品历史序列化器"""
        serializer = UserDishHistorySerializer(self.history)
        data = serializer.data

        self.assertEqual(data['id'], self.history.id)
        # 检查基本字段，根据序列化器定义
        self.assertEqual(data['count'], 5)


class SerializerValidationTest(TestCase):
    """序列化器验证测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')

    def test_dish_serializer_validation(self):
        """测试菜品序列化器验证"""
        # 测试负价格
        serializer = DishSerializer(data={
            'name': '测试菜品',
            'price': -10.0,
            'canteen': self.canteen.id
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_rating_serializer_validation(self):
        """测试评分序列化器验证"""
        # 需要查看 RatingSerializer 的验证逻辑
        # 这里只是基本结构测试
        user = AuthUser.objects.create_user(
            username='testuser2',
            password='testpass'
        )
        dish = Dish.objects.create(
            name='测试菜品2',
            price=Decimal('10.00'),
            canteen=self.canteen
        )

        # 测试有效的评分
        serializer = RatingSerializer(data={
            'user': user.id,
            'dish': dish.id,
            'score': 4.5
        })
        self.assertTrue(serializer.is_valid())


class SerializerFieldTest(TestCase):
    """序列化器字段测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )

    def test_dish_serializer_readonly_fields(self):
        """测试菜品序列化器的只读字段"""
        # 创建序列化器实例
        serializer = DishSerializer(self.dish)

        # 检查只读字段是否存在
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)


    def test_canteen_serializer_meta_fields(self):
        """测试食堂序列化器的元字段"""
        serializer = CanteenSerializer(self.canteen)
        data = serializer.data

        # 检查是否有创建和更新时间
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
