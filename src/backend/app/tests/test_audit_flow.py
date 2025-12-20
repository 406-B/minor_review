import pytest
from post.models import Post, Comment
from list.models import Review, Dish, Tag

@pytest.mark.django_db
class TestAuditFlow:
    """
    集成测试：内容审核流程
    """

    @pytest.fixture
    def admin_client(self, api_client):
        """创建一个管理员用户并返回已认证的客户端"""
        from django.contrib.auth.models import User as AuthUser
        from login.models import User as LoginUser
        from utils.jwt import generate_jwt, encrypt_password
        
        # 创建管理员用户
        username = 'adminuser'
        password = 'password123'
        
        # Auth User (Django内置用户，用于权限检查)
        auth_user = AuthUser.objects.create_superuser(username=username, password=password, email='admin@example.com')
        
        # Login User (业务用户，用于JWT认证)
        login_user = LoginUser.objects.create(
            id=auth_user.id,
            username=username,
            password=encrypt_password(password),
            nickname='Admin User'
        )
        
        # 生成 Token
        payload = {'user_id': login_user.id, 'username': login_user.username}
        token = generate_jwt(payload)
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return api_client

    def test_get_pending_contents(self, admin_client, test_user, sample_dish):
        """测试获取待审核内容"""
        # 创建待审核帖子
        from login.models import User
        # 确保 test_user 对应的 login.User 存在
        if not User.objects.filter(username=test_user.username).exists():
            from utils.jwt import encrypt_password
            User.objects.create(
                id=test_user.id,
                username=test_user.username,
                password=encrypt_password('password123'),
                nickname='Test User'
            )
        login_user = User.objects.get(username=test_user.username)
        
        Post.objects.create(
            author=login_user,
            dish=sample_dish,
            subject="待审核帖子",
            content="内容",
            status='pending'
        )
        
        url = '/api/v1/audit/pending'
        response = admin_client.get(url)
        
        assert response.status_code == 200
        assert response.data['code'] == 200
        contents = response.data['data']['pending_contents']
        assert len(contents) > 0
        assert contents[0]['type'] == 'post'
        assert contents[0]['title'] == '待审核帖子'

    def test_audit_post_approve(self, admin_client, test_user, sample_dish):
        """测试审核通过帖子"""
        from login.models import User
        # 确保 test_user 对应的 login.User 存在
        if not User.objects.filter(username=test_user.username).exists():
            from utils.jwt import encrypt_password
            User.objects.create(
                id=test_user.id,
                username=test_user.username,
                password=encrypt_password('password123'),
                nickname='Test User'
            )
        login_user = User.objects.get(username=test_user.username)
        
        post = Post.objects.create(
            author=login_user,
            dish=sample_dish,
            subject="待审核帖子",
            content="内容",
            status='pending'
        )
        
        url = f'/api/v1/audit/post/{post.id}'
        data = {'action': 'approve'}
        
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == 200
        
        post.refresh_from_db()
        assert post.status == 'approved'

    def test_audit_post_reject(self, admin_client, test_user, sample_dish):
        """测试审核拒绝帖子"""
        from login.models import User
        # 确保 test_user 对应的 login.User 存在
        if not User.objects.filter(username=test_user.username).exists():
            from utils.jwt import encrypt_password
            User.objects.create(
                id=test_user.id,
                username=test_user.username,
                password=encrypt_password('password123'),
                nickname='Test User'
            )
        login_user = User.objects.get(username=test_user.username)
        
        post = Post.objects.create(
            author=login_user,
            dish=sample_dish,
            subject="违规帖子",
            content="内容",
            status='pending'
        )
        
        url = f'/api/v1/audit/post/{post.id}'
        data = {'action': 'reject', 'reason': '内容违规'}
        
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == 200
        
        post.refresh_from_db()
        assert post.status == 'rejected'
        assert post.audit_reason == '内容违规'

    def test_audit_tag_approve(self, admin_client, sample_dish):
        """测试审核通过标签"""
        tag = Tag.objects.create(name="新标签")
        sample_dish.pending_tags.add(tag)
        
        content_id = f"{sample_dish.id}_{tag.id}"
        url = f'/api/v1/audit/tag/{content_id}'
        data = {'action': 'approve'}
        
        response = admin_client.post(url, data, format='json')
        
        # 之前失败是因为 admin_client 创建的用户可能没有 is_staff=True
        # 检查 admin_client fixture
        assert response.status_code == 200
        
        # 验证标签已移动到正式标签列表
        assert tag in sample_dish.tags.all()
        assert tag not in sample_dish.pending_tags.all()

    def test_non_admin_access(self, auth_client):
        """测试非管理员访问审核接口"""
        url = '/api/v1/audit/pending'
        response = auth_client.get(url)
        
        assert response.status_code == 403
