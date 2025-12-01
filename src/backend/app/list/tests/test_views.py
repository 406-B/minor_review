"""
集成测试：List App Views
测试API端点的完整请求-响应流程
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal

from list.models import Canteen, Dish, Tag, Rating, Review, Floor, Window


class CanteenViewsTest(APITestCase):
    """食堂相关视图集成测试"""

    def setUp(self):
        self.client = APIClient()
        self.canteen1 = Canteen.objects.create(
            name='清华园食堂',
            address='清华大学校内'
        )
        self.canteen2 = Canteen.objects.create(
            name='紫荆园食堂',
            address='清华大学校内'
        )

    def test_canteen_list_endpoint(self):
        """测试食堂列表接口"""
        response = self.client.get('/api/canteens/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 2)

    def test_canteen_list_search(self):
        """测试食堂搜索功能"""
        response = self.client.get('/api/canteens/', {'search': '清华园'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '清华园食堂')

    def test_canteen_list_ordering(self):
        """测试食堂排序功能"""
        # 按名称排序
        response = self.client.get('/api/canteens/', {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 按名称逆序
        response = self.client.get('/api/canteens/', {'ordering': '-name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_canteen_detail_endpoint(self):
        """测试食堂详情接口"""
        response = self.client.get(f'/api/canteen/{self.canteen1.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('canteen', response.data['data'])
        self.assertEqual(response.data['data']['canteen']['name'], '清华园食堂')

    def test_canteen_detail_not_found(self):
        """测试获取不存在的食堂"""
        response = self.client.get('/api/canteen/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FloorWindowViewsTest(APITestCase):
    """楼层窗口相关视图测试"""

    def setUp(self):
        self.client = APIClient()
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.floor1 = Floor.objects.create(
            name='一层',
            canteen=self.canteen,
            order=1
        )
        self.window1 = Window.objects.create(
            name='川菜窗口',
            floor=self.floor1,
            order=1
        )

    def test_canteen_floors_endpoint(self):
        """测试获取食堂楼层窗口接口"""
        response = self.client.get(f'/api/canteen/{self.canteen.id}/floors/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertGreater(len(response.data['data']), 0)


class DishViewsTest(APITestCase):
    """菜品相关视图集成测试"""

    def setUp(self):
        self.client = APIClient()
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.tag_spicy = Tag.objects.create(name='辣')
        self.tag_veg = Tag.objects.create(name='素食')

        # 创建多个菜品用于测试
        self.dish1 = Dish.objects.create(
            name='宫保鸡丁',
            description='经典川菜',
            price=Decimal('12.50'),
            canteen=self.canteen,
            rating=Decimal('4.5')
        )
        self.dish1.tags.add(self.tag_spicy)

        self.dish2 = Dish.objects.create(
            name='清炒时蔬',
            description='健康素食',
            price=Decimal('8.00'),
            canteen=self.canteen,
            rating=Decimal('4.0')
        )
        self.dish2.tags.add(self.tag_veg)

    def test_dish_list_endpoint(self):
        """测试菜品列表接口"""
        response = self.client.get('/api/dishes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 2)

    def test_dish_list_filter_by_canteen(self):
        """测试按食堂筛选菜品"""
        response = self.client.get('/api/dishes/', {
            'canteen_id': self.canteen.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    def test_dish_list_filter_by_tag(self):
        """测试按标签筛选菜品"""
        response = self.client.get('/api/dishes/', {
            'tag_ids': [self.tag_spicy.id]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '宫保鸡丁')

    def test_dish_list_filter_by_price_range(self):
        """测试按价格范围筛选"""
        response = self.client.get('/api/dishes/', {
            'min_price': '10.00',
            'max_price': '15.00'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '宫保鸡丁')

    def test_dish_list_filter_by_rating(self):
        """测试按最低评分筛选"""
        response = self.client.get('/api/dishes/', {
            'min_rating': '4.3'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '宫保鸡丁')

    def test_dish_list_search(self):
        """测试菜品搜索功能"""
        response = self.client.get('/api/dishes/', {
            'search': '宫保'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '宫保鸡丁')

    def test_dish_list_ordering_by_rating(self):
        """测试按评分排序"""
        response = self.client.get('/api/dishes/', {
            'ordering': '-rating'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'][0]['name'], '宫保鸡丁')

    def test_dish_list_ordering_by_price(self):
        """测试按价格排序"""
        response = self.client.get('/api/dishes/', {
            'ordering': 'price'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'][0]['name'], '清炒时蔬')

    def test_dish_detail_endpoint(self):
        """测试菜品详情接口"""
        response = self.client.get(f'/api/dish/{self.dish1.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['name'], '宫保鸡丁')

    def test_dish_detail_increments_view_count(self):
        """测试查看菜品详情增加浏览次数"""
        initial_count = self.dish1.view_count

        self.client.get(f'/api/dish/{self.dish1.id}/')

        # 刷新数据库对象
        self.dish1.refresh_from_db()
        self.assertEqual(self.dish1.view_count, initial_count + 1)

    def test_hot_dishes_endpoint(self):
        """测试热门菜品接口"""
        # 增加浏览次数
        self.dish1.view_count = 100
        self.dish1.save()

        response = self.client.get('/api/dishes/hot/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'][0]['name'], '宫保鸡丁')

    def test_new_dishes_endpoint(self):
        """测试新品菜品接口"""
        response = self.client.get('/api/dishes/new/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['data']), 0)


class RatingViewsTest(APITestCase):
    """评分相关视图集成测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )

    def test_rate_dish_success(self):
        """测试成功评分"""
        response = self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {'rating': 4.5},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)

        # 验证菜品评分已更新
        self.dish.refresh_from_db()
        self.assertEqual(float(self.dish.rating), 4.5)

    def test_rate_dish_updates_average(self):
        """测试多个用户评分后平均分计算"""
        # 第一个用户评分
        self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {'rating': 4.0},
            format='json'
        )

        # 第二个用户评分
        user2 = User.objects.create_user(
            username='user2',
            password='pass2'
        )
        self.client.force_authenticate(user=user2)
        self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {'rating': 5.0},
            format='json'
        )

        # 验证平均分
        self.dish.refresh_from_db()
        self.assertEqual(float(self.dish.rating), 4.5)

    def test_rate_dish_unauthorized(self):
        """测试未登录用户评分"""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {'rating': 4.5},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rate_dish_invalid_range_too_high(self):
        """测试评分过高"""
        response = self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {'rating': 6.0},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_dish_invalid_range_too_low(self):
        """测试评分过低"""
        response = self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {'rating': -1.0},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_dish_missing_rating(self):
        """测试缺少评分参数"""
        response = self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_existing_rating(self):
        """测试更新已有评分"""
        # 第一次评分
        self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {'rating': 3.0},
            format='json'
        )

        # 更新评分
        response = self.client.post(
            f'/api/dish/{self.dish.id}/rate/',
            {'rating': 5.0},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证只有一个评分记录
        ratings = Rating.objects.filter(user=self.user, dish=self.dish)
        self.assertEqual(ratings.count(), 1)
        self.assertEqual(float(ratings.first().score), 5.0)


class ReviewViewsTest(APITestCase):
    """评论相关视图集成测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )

    def test_get_review_list(self):
        """测试获取评论列表"""
        # 创建评论
        Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='很好吃'
        )

        response = self.client.get(f'/api/dish/{self.dish.id}/reviews/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']['reviews']), 1)

    def test_create_review_success(self):
        """测试成功创建评论"""
        response = self.client.post(
            f'/api/dish/{self.dish.id}/review/',
            {
                'content': '这道菜很好吃！',
                'images': []
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 201)

        # 验证评论已创建
        reviews = Review.objects.filter(dish=self.dish)
        self.assertEqual(reviews.count(), 1)

    def test_create_review_with_rating(self):
        """测试创建评论同时评分"""
        response = self.client.post(
            f'/api/dish/{self.dish.id}/review/',
            {
                'content': '很好吃',
                'rating_score': 4.5,
                'images': []
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 验证评分也已创建
        rating = Rating.objects.filter(user=self.user, dish=self.dish).first()
        self.assertIsNotNone(rating)
        self.assertEqual(float(rating.score), 4.5)

    def test_prevent_duplicate_review(self):
        """测试防止重复评论"""
        # 创建第一个评论
        Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='第一次评论'
        )

        # 尝试创建第二个评论
        response = self.client.post(
            f'/api/dish/{self.dish.id}/review/',
            {'content': '第二次评论', 'images': []},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_own_review(self):
        """测试更新自己的评论"""
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='原始内容'
        )

        response = self.client.put(
            f'/api/review/{review.id}/',
            {'content': '更新后的内容'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        review.refresh_from_db()
        self.assertEqual(review.content, '更新后的内容')

    def test_cannot_update_others_review(self):
        """测试不能更新他人评论"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass'
        )
        review = Review.objects.create(
            user=other_user,
            dish=self.dish,
            content='别人的评论'
        )

        response = self.client.put(
            f'/api/review/{review.id}/',
            {'content': '尝试修改'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_review(self):
        """测试删除自己的评论"""
        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='要删除的评论'
        )

        response = self.client.delete(f'/api/review/{review.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证评论已删除
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_admin_can_delete_any_review(self):
        """测试管理员可以删除任何评论"""
        admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass'
        )
        self.client.force_authenticate(user=admin_user)

        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='任意用户的评论'
        )

        response = self.client.delete(f'/api/review/{review.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TagViewsTest(APITestCase):
    """标签相关视图集成测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass'
        )
        self.client = APIClient()

        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )
        self.tag = Tag.objects.create(name='辣')

    def test_get_tag_list(self):
        """测试获取标签列表"""
        response = self.client.get('/api/tags/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertGreater(len(response.data['data']), 0)

    def test_add_tag_as_regular_user(self):
        """测试普通用户添加标签到pending_tags"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f'/api/dish/{self.dish.id}/add-tag/',
            {'tag_ids': [self.tag.id]},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('审核', response.data['message'])

        # 验证标签在pending_tags中
        self.assertIn(self.tag, self.dish.pending_tags.all())

    def test_add_tag_as_admin(self):
        """测试管理员直接添加标签"""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f'/api/dish/{self.dish.id}/add-tag/',
            {'tag_ids': [self.tag.id]},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证标签直接在tags中
        self.assertIn(self.tag, self.dish.tags.all())

    def test_approve_pending_tags(self):
        """测试管理员审核标签"""
        self.client.force_authenticate(user=self.admin)

        # 先添加到pending_tags
        self.dish.pending_tags.add(self.tag)

        response = self.client.post(
            f'/api/dish/{self.dish.id}/approve-tags/',
            {'tag_ids': [self.tag.id]},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证标签已移到tags中
        self.dish.refresh_from_db()
        self.assertIn(self.tag, self.dish.tags.all())
        self.assertNotIn(self.tag, self.dish.pending_tags.all())

    def test_reject_pending_tags(self):
        """测试管理员拒绝标签"""
        self.client.force_authenticate(user=self.admin)

        # 先添加到pending_tags
        self.dish.pending_tags.add(self.tag)

        response = self.client.post(
            f'/api/dish/{self.dish.id}/reject-tags/',
            {'tag_ids': [self.tag.id]},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证标签已从pending_tags移除
        self.dish.refresh_from_db()
        self.assertNotIn(self.tag, self.dish.pending_tags.all())
        self.assertNotIn(self.tag, self.dish.tags.all())

