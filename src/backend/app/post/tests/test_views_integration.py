"""
集成测试：Post App Views
测试帖子相关API端点的完整请求-响应流程
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from post.models import Post, Comment
from list.models import Canteen, Dish


class PostViewsIntegrationTest(APITestCase):
    """帖子相关视图集成测试"""

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
            price=10.00,
            canteen=self.canteen
        )

    def test_get_posts_list(self):
        """测试获取帖子列表"""
        # 创建一些测试帖子
        Post.objects.create(
            author=self.user,
            subject='测试帖子1',
            content='这是第一个测试帖子',
            status='approved'
        )
        Post.objects.create(
            author=self.user,
            subject='测试帖子2',
            content='这是第二个测试帖子',
            status='approved'
        )

        response = self.client.get('/api/posts/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 2)

    def test_create_post_success(self):
        """测试成功创建帖子"""
        self.client.force_authenticate(user=self.user)

        post_data = {
            'subject': '我的美食分享',
            'content': '今天吃到了很棒的宫保鸡丁！',
            'images': ['image1.jpg', 'image2.jpg'],
            'dish_id': self.dish.id
        }

        response = self.client.post(
            '/api/posts/',
            post_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 201)

        # 验证帖子已创建
        post = Post.objects.filter(subject='我的美食分享').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.status, 'pending')  # 默认待审核

    def test_create_post_unauthorized(self):
        """测试未登录用户创建帖子"""
        post_data = {
            'subject': '未授权创建',
            'content': '这应该失败'
        }

        response = self.client.post(
            '/api/posts/',
            post_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_missing_required_fields(self):
        """测试创建帖子缺少必填字段"""
        self.client.force_authenticate(user=self.user)

        # 缺少subject
        post_data = {
            'content': '只有内容没有标题'
        }

        response = self.client.post(
            '/api/posts/',
            post_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_post_detail(self):
        """测试获取帖子详情"""
        post = Post.objects.create(
            author=self.user,
            subject='测试帖子详情',
            content='测试内容',
            status='approved'
        )

        response = self.client.get(f'/api/posts/{post.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['subject'], '测试帖子详情')

    def test_update_own_post(self):
        """测试更新自己的帖子"""
        self.client.force_authenticate(user=self.user)

        post = Post.objects.create(
            author=self.user,
            subject='原始标题',
            content='原始内容',
            status='approved'
        )

        update_data = {
            'subject': '更新后的标题',
            'content': '更新后的内容'
        }

        response = self.client.put(
            f'/api/posts/{post.id}/',
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证帖子已更新
        post.refresh_from_db()
        self.assertEqual(post.subject, '更新后的标题')
        self.assertEqual(post.content, '更新后的内容')

    def test_cannot_update_others_post(self):
        """测试不能更新他人的帖子"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass'
        )

        post = Post.objects.create(
            author=other_user,
            subject='别人的帖子',
            content='不能修改',
            status='approved'
        )

        self.client.force_authenticate(user=self.user)

        update_data = {
            'subject': '尝试修改'
        }

        response = self.client.put(
            f'/api/posts/{post.id}/',
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_post(self):
        """测试管理员可以更新任何帖子"""
        self.client.force_authenticate(user=self.admin)

        post = Post.objects.create(
            author=self.user,
            subject='用户帖子',
            content='管理员可以修改',
            status='approved'
        )

        update_data = {
            'subject': '管理员修改的标题'
        }

        response = self.client.put(
            f'/api/posts/{post.id}/',
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        post.refresh_from_db()
        self.assertEqual(post.subject, '管理员修改的标题')

    def test_delete_own_post(self):
        """测试删除自己的帖子"""
        self.client.force_authenticate(user=self.user)

        post = Post.objects.create(
            author=self.user,
            subject='要删除的帖子',
            content='删除我吧',
            status='approved'
        )

        response = self.client.delete(f'/api/posts/{post.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证帖子已删除
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_admin_can_delete_any_post(self):
        """测试管理员可以删除任何帖子"""
        self.client.force_authenticate(user=self.admin)

        post = Post.objects.create(
            author=self.user,
            subject='任意帖子',
            content='管理员可以删除',
            status='approved'
        )

        response = self.client.delete(f'/api/posts/{post.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_like_post(self):
        """测试点赞帖子"""
        self.client.force_authenticate(user=self.user)

        post = Post.objects.create(
            author=self.admin,  # 用管理员创建，避免自赞
            subject='测试点赞',
            content='点赞我吧',
            status='approved'
        )

        response = self.client.post(f'/api/posts/{post.id}/like/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证点赞记录
        self.assertTrue(post.likes.filter(id=self.user.id).exists())

    def test_unlike_post(self):
        """测试取消点赞"""
        self.client.force_authenticate(user=self.user)

        post = Post.objects.create(
            author=self.admin,
            subject='测试取消点赞',
            content='取消点赞',
            status='approved'
        )

        # 先点赞
        post.likes.add(self.user)

        response = self.client.post(f'/api/posts/{post.id}/unlike/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(post.likes.filter(id=self.user.id).exists())


class CommentViewsIntegrationTest(APITestCase):
    """评论相关视图集成测试"""

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='pass'
        )

        # 创建帖子
        self.post = Post.objects.create(
            author=self.other_user,
            subject='测试帖子',
            content='用于测试评论',
            status='approved'
        )

    def test_create_comment_success(self):
        """测试成功创建评论"""
        self.client.force_authenticate(user=self.user)

        comment_data = {
            'content': '这是一条测试评论',
            'images': []
        }

        response = self.client.post(
            f'/api/posts/{self.post.id}/comments/',
            comment_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 201)

        # 验证评论已创建
        comment = Comment.objects.filter(post=self.post).first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, '这是一条测试评论')

    def test_get_comments_list(self):
        """测试获取评论列表"""
        # 创建多条评论
        Comment.objects.create(
            author=self.user,
            post=self.post,
            content='第一条评论'
        )
        Comment.objects.create(
            author=self.other_user,
            post=self.post,
            content='第二条评论'
        )

        response = self.client.get(f'/api/posts/{self.post.id}/comments/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    def test_update_own_comment(self):
        """测试更新自己的评论"""
        self.client.force_authenticate(user=self.user)

        comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            content='原始评论'
        )

        update_data = {
            'content': '更新后的评论'
        }

        response = self.client.put(
            f'/api/comments/{comment.id}/',
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment.refresh_from_db()
        self.assertEqual(comment.content, '更新后的评论')

    def test_delete_own_comment(self):
        """测试删除自己的评论"""
        self.client.force_authenticate(user=self.user)

        comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            content='要删除的评论'
        )

        response = self.client.delete(f'/api/comments/{comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_reply_to_comment(self):
        """测试回复评论"""
        self.client.force_authenticate(user=self.user)

        parent_comment = Comment.objects.create(
            author=self.other_user,
            post=self.post,
            content='父评论'
        )

        reply_data = {
            'content': '这是回复',
            'parent_id': parent_comment.id
        }

        response = self.client.post(
            f'/api/posts/{self.post.id}/comments/',
            reply_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reply = Comment.objects.filter(parent=parent_comment).first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.content, '这是回复')
