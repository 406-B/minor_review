"""
单元测试：List App Models
测试食堂、菜品、标签、评分、评论等模型
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from decimal import Decimal

from list.models import Canteen, Dish, Tag, Rating, Review, Floor, Window


class CanteenModelTest(TestCase):
    """食堂模型测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(
            name='清华园食堂',
            latitude=Decimal('40.0027'),
            longitude=Decimal('116.3264'),
            address='清华大学校内'
        )

    def test_canteen_creation(self):
        """测试食堂创建"""
        self.assertEqual(self.canteen.name, '清华园食堂')
        self.assertIsNotNone(self.canteen.created_at)
        self.assertIsNotNone(self.canteen.updated_at)

    def test_canteen_str_representation(self):
        """测试字符串表示"""
        self.assertEqual(str(self.canteen), '清华园食堂')

    def test_canteen_unique_name(self):
        """测试食堂名称唯一性"""
        with self.assertRaises(Exception):
            Canteen.objects.create(name='清华园食堂')


class FloorModelTest(TestCase):
    """楼层模型测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.floor = Floor.objects.create(
            name='一层',
            canteen=self.canteen,
            order=1
        )

    def test_floor_creation(self):
        """测试楼层创建"""
        self.assertEqual(self.floor.name, '一层')
        self.assertEqual(self.floor.canteen, self.canteen)
        self.assertEqual(self.floor.order, 1)

    def test_floor_str_representation(self):
        """测试字符串表示"""
        expected = f"{self.canteen.name} - {self.floor.name}"
        self.assertEqual(str(self.floor), expected)


class WindowModelTest(TestCase):
    """窗口模型测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.floor = Floor.objects.create(name='一层', canteen=self.canteen)
        self.window = Window.objects.create(
            name='川菜窗口',
            floor=self.floor,
            order=1
        )

    def test_window_creation(self):
        """测试窗口创建"""
        self.assertEqual(self.window.name, '川菜窗口')
        self.assertEqual(self.window.floor, self.floor)

    def test_window_str_representation(self):
        """测试字符串表示"""
        expected = f"{self.canteen.name}-{self.floor.name}-{self.window.name}"
        self.assertEqual(str(self.window), expected)


class TagModelTest(TestCase):
    """标签模型测试"""

    def test_tag_creation(self):
        """测试标签创建"""
        tag = Tag.objects.create(name='辣')
        self.assertEqual(tag.name, '辣')
        self.assertIsNotNone(tag.created_at)

    def test_tag_unique_name(self):
        """测试标签名称唯一性"""
        Tag.objects.create(name='辣')
        with self.assertRaises(Exception):
            Tag.objects.create(name='辣')

    def test_tag_str_representation(self):
        """测试字符串表示"""
        tag = Tag.objects.create(name='素食')
        self.assertEqual(str(tag), '素食')


class DishModelTest(TestCase):
    """菜品模型测试"""

    def setUp(self):
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.tag_spicy = Tag.objects.create(name='辣')
        self.tag_veg = Tag.objects.create(name='素食')

        self.dish = Dish.objects.create(
            name='宫保鸡丁',
            description='经典川菜',
            price=Decimal('12.50'),
            canteen=self.canteen
        )
        self.dish.tags.add(self.tag_spicy)

    def test_dish_creation(self):
        """测试菜品创建"""
        self.assertEqual(self.dish.name, '宫保鸡丁')
        self.assertEqual(self.dish.price, Decimal('12.50'))
        self.assertEqual(self.dish.canteen, self.canteen)
        self.assertEqual(self.dish.rating, Decimal('0.0'))
        self.assertEqual(self.dish.view_count, 0)

    def test_dish_str_representation(self):
        """测试字符串表示"""
        expected = f"{self.dish.name} - {self.canteen.name}"
        self.assertEqual(str(self.dish), expected)

    def test_increment_view_count(self):
        """测试浏览次数增加"""
        initial_count = self.dish.view_count
        self.dish.increment_view_count()
        self.assertEqual(self.dish.view_count, initial_count + 1)

        # 再次增加
        self.dish.increment_view_count()
        self.assertEqual(self.dish.view_count, initial_count + 2)

    def test_price_cannot_be_negative(self):
        """测试价格不能为负数"""
        dish = Dish(
            name='测试菜品',
            price=Decimal('-10.00'),
            canteen=self.canteen
        )
        with self.assertRaises(ValidationError):
            dish.full_clean()

    def test_rating_range_validation(self):
        """测试评分范围验证（0-5）"""
        # 测试超出上限
        self.dish.rating = Decimal('6.0')
        with self.assertRaises(ValidationError):
            self.dish.full_clean()

        # 测试低于下限
        self.dish.rating = Decimal('-1.0')
        with self.assertRaises(ValidationError):
            self.dish.full_clean()

        # 测试有效范围
        self.dish.rating = Decimal('4.5')
        self.dish.full_clean()  # 应该不抛出异常

    def test_dish_tags_relationship(self):
        """测试菜品和标签的多对多关系"""
        self.assertEqual(self.dish.tags.count(), 1)
        self.dish.tags.add(self.tag_veg)
        self.assertEqual(self.dish.tags.count(), 2)

        # 测试反向查询
        dishes = self.tag_spicy.dishes.all()
        self.assertIn(self.dish, dishes)

    def test_pending_tags_relationship(self):
        """测试待审核标签关系"""
        pending_tag = Tag.objects.create(name='新标签')
        self.dish.pending_tags.add(pending_tag)
        self.assertEqual(self.dish.pending_tags.count(), 1)

        # 待审核标签不应该在正式标签中
        self.assertNotIn(pending_tag, self.dish.tags.all())


class RatingModelTest(TestCase):
    """评分模型测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
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
        self.assertIsNotNone(rating.created_at)

    def test_unique_user_dish_rating(self):
        """测试同一用户对同一菜品只能有一个评分"""
        Rating.objects.create(
            user=self.user,
            dish=self.dish,
            score=Decimal('4.0')
        )

        # 尝试创建重复评分应该失败
        with self.assertRaises(Exception):
            Rating.objects.create(
                user=self.user,
                dish=self.dish,
                score=Decimal('5.0')
            )

    def test_score_range_validation(self):
        """测试评分必须在1-5之间"""
        # 测试低于最小值
        rating = Rating(
            user=self.user,
            dish=self.dish,
            score=Decimal('0.5')
        )
        with self.assertRaises(ValidationError):
            rating.full_clean()

        # 测试超过最大值
        rating.score = Decimal('5.5')
        with self.assertRaises(ValidationError):
            rating.full_clean()

        # 测试有效值
        rating.score = Decimal('3.5')
        rating.full_clean()  # 应该不抛出异常

    def test_rating_str_representation(self):
        """测试字符串表示"""
        rating = Rating.objects.create(
            user=self.user,
            dish=self.dish,
            score=Decimal('4.5')
        )
        expected = f"{self.user.username} - {self.dish.name}: 4.5分"
        self.assertEqual(str(rating), expected)


class ReviewModelTest(TestCase):
    """评论模型测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
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
            content='这道菜很好吃！'
        )
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.dish, self.dish)
        self.assertEqual(review.content, '这道菜很好吃！')
        self.assertEqual(review.likes_count, 0)

    def test_review_creation_with_images(self):
        """测试带图片的评论创建"""
        images = [
            'http://example.com/image1.jpg',
            'http://example.com/image2.jpg'
        ]
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='有图有真相',
            images=images
        )
        self.assertEqual(len(review.images), 2)
        self.assertIn('http://example.com/image1.jpg', review.images)

    def test_review_with_rating(self):
        """测试评论关联评分"""
        rating = Rating.objects.create(
            user=self.user,
            dish=self.dish,
            score=Decimal('4.5')
        )
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='好吃',
            rating=rating
        )
        self.assertEqual(review.rating, rating)

    def test_likes_count_default_value(self):
        """测试点赞数默认为0"""
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='测试'
        )
        self.assertEqual(review.likes_count, 0)

    def test_review_str_representation(self):
        """测试字符串表示"""
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='这是一段很长的评论内容，用来测试字符串表示是否会被截断显示'
        )
        str_repr = str(review)
        self.assertIn(self.user.username, str_repr)
        self.assertIn(self.dish.name, str_repr)
        # 应该只显示前50个字符
        self.assertLessEqual(len(str_repr), 100)

    def test_images_default_value(self):
        """测试图片列表默认为空列表"""
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='无图评论'
        )
        self.assertEqual(review.images, [])
        self.assertIsInstance(review.images, list)

