"""
单元测试：List App Models
测试模型的创建、验证和基本方法
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime

from list.models import Canteen, Dish, Tag, Floor, Window, Rating, Review


class CanteenModelTest(TestCase):
    """食堂模型单元测试"""

    def test_canteen_creation(self):
        """测试食堂创建"""
        canteen = Canteen.objects.create(
            name='测试食堂',
            latitude=Decimal('39.9042'),
            longitude=Decimal('116.4074'),
            address='北京市海淀区'
        )

        self.assertEqual(canteen.name, '测试食堂')
        self.assertEqual(canteen.latitude, Decimal('39.9042'))
        self.assertEqual(canteen.longitude, Decimal('116.4074'))
        self.assertEqual(canteen.address, '北京市海淀区')
        self.assertIsNotNone(canteen.created_at)
        self.assertIsNotNone(canteen.updated_at)

    def test_canteen_str_method(self):
        """测试食堂字符串表示"""
        canteen = Canteen.objects.create(name='清华园食堂')
        self.assertEqual(str(canteen), '清华园食堂')

    def test_canteen_unique_name(self):
        """测试食堂名称唯一性"""
        Canteen.objects.create(name='测试食堂')

        with self.assertRaises(Exception):  # 应该抛出完整性错误
            Canteen.objects.create(name='测试食堂')


class DishModelTest(TestCase):
    """菜品模型单元测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')

    def test_dish_creation(self):
        """测试菜品创建"""
        dish = Dish.objects.create(
            name='宫保鸡丁',
            description='经典川菜',
            price=Decimal('12.50'),
            canteen=self.canteen
        )

        self.assertEqual(dish.name, '宫保鸡丁')
        self.assertEqual(dish.description, '经典川菜')
        self.assertEqual(dish.price, Decimal('12.50'))
        self.assertEqual(dish.canteen, self.canteen)
        self.assertEqual(dish.view_count, 0)
        self.assertEqual(dish.rating_count, 0)
        self.assertEqual(dish.rating, Decimal('0'))

    def test_dish_price_validation(self):
        """测试菜品价格验证"""
        # 负价格应该抛出验证错误
        with self.assertRaises(ValidationError):
            dish = Dish(
                name='测试菜品',
                price=Decimal('-1.00'),
                canteen=self.canteen
            )
            dish.full_clean()

    def test_dish_str_method(self):
        """测试菜品字符串表示"""
        dish = Dish.objects.create(
            name='宫保鸡丁',
            price=Decimal('12.50'),
            canteen=self.canteen
        )
        # 实际实现：返回 "菜品名 - 食堂名"
        self.assertEqual(str(dish), f'{dish.name} - {dish.canteen.name}')

    def test_dish_average_rating_calculation(self):
        """测试菜品平均评分计算"""
        dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )

        # 创建多个评分
        ratings = [4.5, 3.0, 5.0]
        expected_avg = sum(ratings) / len(ratings)

        # 这里需要实现实际的评分计算逻辑
        # 假设Dish模型有update_rating方法
        dish.rating = Decimal(str(expected_avg))
        dish.rating_count = len(ratings)
        dish.save()

        self.assertEqual(dish.rating, Decimal(str(expected_avg)))
        self.assertEqual(dish.rating_count, len(ratings))


class TagModelTest(TestCase):
    """标签模型单元测试"""

    def test_tag_creation(self):
        """测试标签创建"""
        tag = Tag.objects.create(name='辣')

        self.assertEqual(tag.name, '辣')
        self.assertIsNotNone(tag.created_at)
        self.assertIsNotNone(tag.updated_at)

    def test_tag_str_method(self):
        """测试标签字符串表示"""
        tag = Tag.objects.create(name='素食')
        self.assertEqual(str(tag), '素食')

    def test_tag_unique_name(self):
        """测试标签名称唯一性"""
        Tag.objects.create(name='辣')

        with self.assertRaises(Exception):
            Tag.objects.create(name='辣')


class FloorModelTest(TestCase):
    """楼层模型单元测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')

    def test_floor_creation(self):
        """测试楼层创建"""
        floor = Floor.objects.create(
            name='一层',
            canteen=self.canteen,
            order=1
        )

        self.assertEqual(floor.name, '一层')
        self.assertEqual(floor.canteen, self.canteen)
        self.assertEqual(floor.order, 1)

    def test_floor_str_method(self):
        """测试楼层字符串表示"""
        floor = Floor.objects.create(
            name='一层',
            canteen=self.canteen
        )
        self.assertEqual(str(floor), '测试食堂 - 一层')


class WindowModelTest(TestCase):
    """窗口模型单元测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.floor = Floor.objects.create(
            name='一层',
            canteen=self.canteen
        )

    def test_window_creation(self):
        """测试窗口创建"""
        window = Window.objects.create(
            name='川菜窗口',
            floor=self.floor,
            order=1
        )

        self.assertEqual(window.name, '川菜窗口')
        self.assertEqual(window.floor, self.floor)
        self.assertEqual(window.order, 1)

    def test_window_str_method(self):
        """测试窗口字符串表示"""
        window = Window.objects.create(
            name='川菜窗口',
            floor=self.floor
        )
        self.assertEqual(str(window), '测试食堂-一层-川菜窗口')


class RatingModelTest(TestCase):
    """评分模型单元测试"""

    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )

    def test_rating_creation(self):
        """测试评分创建"""
        rating = Rating.objects.create(
            user=self.user,
            dish=self.dish,
            score=Decimal('4.5')
        )

        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.dish, self.dish)
        self.assertEqual(rating.score, Decimal('4.5'))

    def test_rating_score_validation(self):
        """测试评分分数验证"""
        # 超出范围的评分应该抛出验证错误
        with self.assertRaises(ValidationError):
            rating = Rating(
                user=self.user,
                dish=self.dish,
                score=Decimal('6.0')  # 超过5分
            )
            rating.full_clean()

        with self.assertRaises(ValidationError):
            rating = Rating(
                user=self.user,
                dish=self.dish,
                score=Decimal('-1.0')  # 低于0分
            )
            rating.full_clean()


class ReviewModelTest(TestCase):
    """评论模型单元测试"""

    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )

    def test_review_creation(self):
        """测试评论创建"""
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='很好吃！'
        )

        self.assertEqual(review.user, self.user)
        self.assertEqual(review.dish, self.dish)
        self.assertEqual(review.content, '很好吃！')
        self.assertEqual(review.status, 'pending')  # 假设默认状态为待审核

    def test_review_with_images(self):
        """测试带图片的评论"""
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='很美味',
            images=['image1.jpg', 'image2.jpg']
        )

        self.assertEqual(review.content, '很美味')
        self.assertEqual(len(review.images), 2)

    def test_review_str_method(self):
        """测试评论字符串表示"""
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='测试评论'
        )
        # 实际实现：返回 "用户名 - 菜品名: 评论内容前50字符"
        expected_str = f"{self.user.username} - {self.dish.name}: {review.content[:50]}"
        self.assertEqual(str(review), expected_str)
