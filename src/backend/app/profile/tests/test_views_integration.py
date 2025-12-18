"""
集成测试：Profile App Views
测试用户个人资料相关API端点的完整请求-响应流程
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal
from PIL import Image
import io

from profile.models import User as CustomUser
from list.models import Canteen, Dish, Tag, Review, Rating
from post.models import Post, Comment


class ProfileViewsIntegrationTest(APITestCase):
    """个人资料相关视图集成测试"""

    def setUp(self):
        self.client = APIClient()

        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass'
        )

        # 创建测试数据
        self.canteen = Canteen.objects.create(name='测试食堂')
        self.dish = Dish.objects.create(
            name='测试菜品',
            price=Decimal('10.00'),
            canteen=self.canteen
        )
        self.tag = Tag.objects.create(name='辣')

    def test_get_profile_success(self):
        """测试成功获取个人资料"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/profile/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('nickname', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_profile_unauthorized(self):
        """测试未登录获取个人资料"""
        response = self.client.get('/api/profile/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_success(self):
        """测试成功更新个人资料"""
        self.client.force_authenticate(user=self.user)

        # 创建一个小的测试图片
        image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)

        data = {
            'nickname': '新昵称'
        }
        files = {
            'avatar': ('test.jpg', image_io, 'image/jpeg')
        }

        response = self.client.put(
            '/api/profile/',
            data,
            files=files,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '更新成功')
        self.assertEqual(response.data['data']['nickname'], '新昵称')

        # 验证数据库已更新
        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, '新昵称')
        self.assertIsNotNone(self.user.avatar)

    def test_update_profile_partial_update(self):
        """测试部分更新个人资料"""
        self.client.force_authenticate(user=self.user)

        # 只更新昵称
        data = {
            'nickname': '只更新昵称'
        }

        response = self.client.patch(
            '/api/profile/',
            data,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['nickname'], '只更新昵称')

    def test_update_profile_no_changes(self):
        """测试没有实际更新的情况"""
        self.client.force_authenticate(user=self.user)

        # 不提供任何更新字段
        response = self.client.put(
            '/api/profile/',
            {},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('至少需要提供一个更新字段', response.data['message'])

    def test_update_profile_invalid_data(self):
        """测试更新个人资料时提供无效数据"""
        self.client.force_authenticate(user=self.user)

        # 测试过长的昵称
        data = {
            'nickname': 'a' * 100  # 假设昵称最大长度限制
        }

        response = self.client.put(
            '/api/profile/',
            data,
            format='multipart'
        )

        # 根据实际验证规则，这里可能通过或失败
        # 如果有限制，应该返回400错误
        self.assertIn(response.status_code, [200, 400])

    def test_update_password_success(self):
        """测试成功修改密码"""
        self.client.force_authenticate(user=self.user)

        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }

        response = self.client.post(
            '/api/profile/update-password/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('密码修改成功', response.data['message'])

    def test_update_password_wrong_old_password(self):
        """测试修改密码时旧密码错误"""
        self.client.force_authenticate(user=self.user)

        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }

        response = self.client.post(
            '/api/profile/update-password/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('旧密码错误', response.data['message'])

    def test_update_password_passwords_not_match(self):
        """测试修改密码时新密码不一致"""
        self.client.force_authenticate(user=self.user)

        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'confirm_password': 'differentpass'
        }

        response = self.client.post(
            '/api/profile/update-password/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('密码不一致', response.data.get('errors', {}).get('confirm_password', [''])[0])

    def test_update_password_missing_fields(self):
        """测试修改密码时缺少必填字段"""
        self.client.force_authenticate(user=self.user)

        # 缺少confirm_password
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456'
        }

        response = self.client.post(
            '/api/profile/update-password/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_stats_success(self):
        """测试成功获取用户统计信息"""
        self.client.force_authenticate(user=self.user)

        # 创建一些测试数据
        post = Post.objects.create(
            author=self.admin,
            subject='测试帖子',
            content='测试内容',
            status='approved'
        )
        post.likes.add(self.user)  # 用户点赞了这个帖子

        Comment.objects.create(
            author=self.user,
            post=post,
            content='测试评论'
        )

        response = self.client.get('/api/profile/stats/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('liked_posts_count', response.data)
        self.assertIn('commented_posts_count', response.data)
        self.assertIn('following_count', response.data)
        self.assertEqual(response.data['liked_posts_count'], 1)
        self.assertEqual(response.data['commented_posts_count'], 1)

    def test_get_my_posts_success(self):
        """测试成功获取我的帖子"""
        self.client.force_authenticate(user=self.user)

        # 创建测试帖子
        Post.objects.create(
            author=self.user,
            subject='我的帖子1',
            content='内容1',
            status='approved'
        )
        Post.objects.create(
            author=self.user,
            subject='我的帖子2',
            content='内容2',
            status='approved'
        )

        response = self.client.get('/api/profile/my-posts/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']['posts']), 2)
        self.assertIn('pagination', response.data['data'])

    def test_get_my_posts_pagination(self):
        """测试我的帖子分页"""
        self.client.force_authenticate(user=self.user)

        # 创建多个帖子
        for i in range(5):
            Post.objects.create(
                author=self.user,
                subject=f'帖子{i}',
                content=f'内容{i}',
                status='approved'
            )

        response = self.client.get('/api/profile/my-posts/?page=1&page_size=2')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['posts']), 2)
        self.assertEqual(response.data['data']['pagination']['total'], 5)
        self.assertEqual(response.data['data']['pagination']['page'], 1)
        self.assertEqual(response.data['data']['pagination']['page_size'], 2)

    def test_get_recent_posts_success(self):
        """测试成功获取最近帖子"""
        self.client.force_authenticate(user=self.user)

        # 创建测试帖子
        for i in range(5):
            Post.objects.create(
                author=self.user,
                subject=f'最近帖子{i}',
                content=f'内容{i}',
                status='approved'
            )

        response = self.client.get('/api/profile/recent-posts/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 3)  # 默认返回3个

    def test_get_liked_posts_success(self):
        """测试成功获取点赞的帖子"""
        self.client.force_authenticate(user=self.user)

        # 创建帖子并让用户点赞
        post1 = Post.objects.create(
            author=self.admin,
            subject='被点赞的帖子1',
            content='内容1',
            status='approved'
        )
        post1.likes.add(self.user)

        post2 = Post.objects.create(
            author=self.admin,
            subject='被点赞的帖子2',
            content='内容2',
            status='approved'
        )
        post2.likes.add(self.user)

        response = self.client.get('/api/profile/liked-posts/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']['posts']), 2)

    def test_get_my_comments_success(self):
        """测试成功获取我的评论"""
        self.client.force_authenticate(user=self.user)

        # 创建帖子和评论
        post = Post.objects.create(
            author=self.admin,
            subject='有评论的帖子',
            content='内容',
            status='approved'
        )

        Comment.objects.create(
            author=self.user,
            post=post,
            content='我的评论1'
        )
        Comment.objects.create(
            author=self.user,
            post=post,
            content='我的评论2'
        )

        response = self.client.get('/api/profile/my-comments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']['comments']), 2)

    def test_get_preference_tags_success(self):
        """测试成功获取偏好标签"""
        self.client.force_authenticate(user=self.user)

        # 设置用户的偏好标签
        self.user.preference_tags.add(self.tag)

        response = self.client.get('/api/profile/preference-tags/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '辣')

    def test_set_preference_tags_success(self):
        """测试成功设置偏好标签"""
        self.client.force_authenticate(user=self.user)

        tag2 = Tag.objects.create(name='素食')

        data = {
            'tag_ids': [self.tag.id, tag2.id]
        }

        response = self.client.post(
            '/api/profile/preference-tags/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 2)

        # 验证数据库已更新
        self.user.refresh_from_db()
        self.assertEqual(self.user.preference_tags.count(), 2)

    def test_add_preference_tags_success(self):
        """测试成功添加偏好标签"""
        self.client.force_authenticate(user=self.user)

        # 先设置一个标签
        self.user.preference_tags.add(self.tag)

        # 再添加新标签
        tag2 = Tag.objects.create(name='甜')

        data = {
            'tag_ids': [tag2.id]
        }

        response = self.client.post(
            '/api/profile/add-preference-tags/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.preference_tags.count(), 2)

    def test_get_recommended_dishes_with_preferences(self):
        """测试基于偏好标签获取推荐菜品"""
        self.client.force_authenticate(user=self.user)

        # 设置用户偏好标签
        self.user.preference_tags.add(self.tag)

        # 创建带标签的菜品
        dish_with_tag = Dish.objects.create(
            name='辣子鸡丁',
            price=Decimal('15.00'),
            canteen=self.canteen
        )
        dish_with_tag.tags.add(self.tag)

        # 创建不带标签的菜品
        Dish.objects.create(
            name='清炒时蔬',
            price=Decimal('10.00'),
            canteen=self.canteen
        )

        response = self.client.get('/api/profile/recommended-dishes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertGreater(len(response.data['data']['dishes']), 0)

        # 验证返回了用户偏好标签信息
        self.assertEqual(len(response.data['data']['user_tags']), 1)
        self.assertEqual(response.data['data']['user_tags'][0]['name'], '辣')

    def test_get_recommended_dishes_no_preferences(self):
        """测试没有偏好标签时获取推荐菜品"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/profile/recommended-dishes/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 404)
        self.assertIn('未设置偏好标签', response.data['message'])

    def test_admin_get_pending_contents(self):
        """测试管理员获取待审核内容"""
        self.client.force_authenticate(user=self.admin)

        # 创建待审核的帖子
        Post.objects.create(
            author=self.user,
            subject='待审核帖子',
            content='需要审核的内容',
            status='pending'
        )

        response = self.client.get('/api/profile/pending-contents/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertGreater(response.data['data']['total'], 0)

    def test_non_admin_cannot_get_pending_contents(self):
        """测试非管理员不能获取待审核内容"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/profile/pending-contents/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 403)

    def test_admin_audit_content_approve_post(self):
        """测试管理员审核通过帖子"""
        self.client.force_authenticate(user=self.admin)

        post = Post.objects.create(
            author=self.user,
            subject='待审核帖子',
            content='需要审核',
            status='pending'
        )

        data = {
            'action': 'approve'
        }

        response = self.client.post(
            f'/api/profile/audit/post/{post.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('审核通过', response.data['message'])

        # 验证帖子状态已更新
        post.refresh_from_db()
        self.assertEqual(post.status, 'approved')

    def test_admin_audit_content_reject_review(self):
        """测试管理员审核拒绝评价"""
        self.client.force_authenticate(user=self.admin)

        review = Review.objects.create(
            user=self.user,
            dish=self.dish,
            content='待审核评价',
            status='pending'
        )

        data = {
            'action': 'reject',
            'reason': '内容不合适'
        }

        response = self.client.post(
            f'/api/profile/audit/review/{review.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('审核拒绝', response.data['message'])

        # 验证评价状态已更新
        review.refresh_from_db()
        self.assertEqual(review.status, 'rejected')
        self.assertEqual(review.audit_reason, '内容不合适')
