import pytest
from post.models import Post, Comment, Like


# 认证标签：集成测试（通过 API + DB 链路验证）
pytestmark = [pytest.mark.integration]

@pytest.mark.django_db
class TestAdvancedPostFlow:
    """
    集成测试：社区帖子高级功能
    """

    def test_delete_post(self, auth_client, test_user, sample_dish):
        """测试删除帖子"""
        # 1. 创建帖子
        # Post.author 是 login.models.User，而 test_user 是 auth.User
        from login.models import User
        login_user = User.objects.get(username=test_user.username)
        
        post = Post.objects.create(
            author=login_user,
            dish=sample_dish,
            subject="待删除帖子",
            content="内容"
        )
        
        # 2. 删除帖子
        url = f'/api/v1/posts/{post.id}/delete/'
        response = auth_client.delete(url)
        
        assert response.status_code == 200
        # JsonResponse returns bytes content, need to parse
        import json
        data = json.loads(response.content)
        assert data['code'] == 200
        
        # 验证数据库
        assert not Post.objects.filter(id=post.id).exists()

    def test_delete_post_permission(self, api_client, test_user, sample_dish):
        """测试删除帖子权限（非作者不能删除）"""
        # 1. 创建帖子
        from login.models import User
        # 确保 login.models.User 存在
        if not User.objects.filter(username=test_user.username).exists():
            from utils.jwt import encrypt_password
            User.objects.create(
                id=test_user.id,
                username=test_user.username,
                password=encrypt_password('password'),
                nickname='Test User'
            )
        login_user = User.objects.get(username=test_user.username)
        
        post = Post.objects.create(
            author=login_user,
            dish=sample_dish,
            subject="别人的帖子",
            content="内容"
        )
        
        # 2. 使用另一个用户登录
        # Create auth user first
        from django.contrib.auth.models import User as AuthUser
        from utils.jwt import encrypt_password
        
        other_auth_user = AuthUser.objects.create_user(username='other', password='password')
        other_user = User.objects.create(
            id=other_auth_user.id,
            username='other', 
            password=encrypt_password('password'),
            nickname='Other'
        )
        
        # 生成 token
        from utils.jwt import generate_jwt
        payload = {'user_id': other_user.id, 'username': other_user.username}
        token = generate_jwt(payload)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 3. 尝试删除
        url = f'/api/v1/posts/{post.id}/delete/'
        response = api_client.delete(url)
        
        assert response.status_code == 403

    def test_toggle_post_like(self, auth_client, test_user, sample_dish):
        """测试点赞/取消点赞"""
        # 1. 创建帖子
        from login.models import User
        # 确保 login.models.User 存在
        if not User.objects.filter(username=test_user.username).exists():
            from utils.jwt import encrypt_password
            User.objects.create(
                id=test_user.id,
                username=test_user.username,
                password=encrypt_password('password'),
                nickname='Test User'
            )
        login_user = User.objects.get(username=test_user.username)
        
        post = Post.objects.create(
            author=login_user,
            dish=sample_dish,
            subject="点赞测试",
            content="内容"
        )
        
        # 2. 点赞
        url = f'/api/v1/posts/{post.id}/like/'
        response = auth_client.post(url)
        
        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        # 修正：后端返回的是 is_liked 而不是 liked
        assert data['data']['is_liked'] is True
        # 修正：Post 模型字段是 likes_count 而不是 like_count
        assert Post.objects.get(id=post.id).likes_count == 1
        
        # 3. 取消点赞
        response = auth_client.post(url)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['data']['is_liked'] is False
        assert Post.objects.get(id=post.id).likes_count == 0

    def test_forum_home(self, auth_client):
        """测试论坛主页"""
        url = '/api/v1/forum/home/'
        response = auth_client.get(url)
        
        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        # The view returns 'posts', 'pagination', 'sort_by' in data
        # It does NOT return 'hot_posts', 'latest_posts', 'hot_dishes' as I assumed.
        # Based on post/views.py:
        # 'data': {
        #     'posts': serializer.data,
        #     'pagination': ...,
        #     'sort_by': ...
        # }
        assert 'posts' in data['data']
        assert 'pagination' in data['data']
        assert 'sort_by' in data['data']

    def test_dish_posts(self, auth_client, sample_dish, test_user):
        """测试获取菜品相关帖子"""
        # 创建一些帖子
        from login.models import User
        login_user = User.objects.get(username=test_user.username)
        
        Post.objects.create(
            author=login_user,
            dish=sample_dish,
            subject="菜品评价1",
            content="好吃"
        )
        
        url = f'/api/v1/dishes/{sample_dish.id}/posts/'
        response = auth_client.get(url)
        
        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert len(data['data']['posts']) > 0
        assert data['data']['dish']['id'] == sample_dish.id
