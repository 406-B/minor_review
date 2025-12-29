import pytest
from post.models import Post, Comment


# 认证标签：集成测试（通过 API + DB 链路验证）
pytestmark = [pytest.mark.integration]

@pytest.mark.django_db
class TestPostFlow:
    """
    集成测试：帖子与社区链路
    """

    def test_create_post(self, auth_client):
        """测试创建帖子"""
        url = '/api/v1/posts/create/'
        # CreatePostSerializer fields: ['subject', 'content', 'images', 'dish']
        # 'subject' is required and max 200 chars
        data = {
            'subject': '测试帖子主题',
            'content': '这是一个测试帖子内容',
            'images': []
        }
        
        response = auth_client.post(url, data, format='json')
        
        # 根据实际 API 实现，可能返回 201 或 200
        if response.status_code == 400:
            print(response.data)
        assert response.status_code in [200, 201]
        if response.status_code == 200:
             # create_post view returns JsonResponse({'code': 200, ...})
             # Wait, create_post view returns PostSerializer(post).data directly?
             # Let's check create_post view again.
             # It returns JsonResponse({'code': 200, 'message': '发布成功', 'data': serializer.data})
             assert response.json()['code'] in [200, 201]
        
        assert Post.objects.filter(subject='测试帖子主题').exists()

    def test_post_list(self, api_client, auth_client):
        """测试获取帖子列表"""
        # 先创建一个帖子
        self.test_create_post(auth_client)
        
        url = '/api/v1/posts/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        # post_list returns JsonResponse({'code': 200, 'data': {'posts': [...]}})
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']['posts']) > 0

    def test_create_comment(self, auth_client):
        """测试创建评论"""
        # 先创建一个帖子
        self.test_create_post(auth_client)
        post = Post.objects.first()
        
        url = '/api/v1/comments/create/'
        # CreateCommentSerializer fields: ['post', 'content', 'images', 'parent']
        # 'post' is a PrimaryKeyRelatedField or similar?
        # Looking at serializer:
        # class CreateCommentSerializer(serializers.ModelSerializer):
        #     class Meta:
        #         model = Comment
        #         fields = ['post', 'content', 'images', 'parent']
        # If 'post' is a ForeignKey, DRF expects 'post' ID by default.
        data = {
            'post': post.id,
            'content': '这是一个测试评论',
            'images': []
        }
        
        response = auth_client.post(url, data, format='json')
        if response.status_code == 400:
            print(response.data)
        assert response.status_code in [200, 201]
        assert Comment.objects.filter(post=post, content='这是一个测试评论').exists()

    def test_post_detail(self, auth_client):
        """测试获取帖子详情"""
        self.test_create_post(auth_client)
        post = Post.objects.first()
        
        url = f'/api/v1/posts/{post.id}/'
        response = auth_client.get(url)
        
        assert response.status_code == 200
        assert response.json()['code'] == 200
        assert response.json()['data']['id'] == post.id

    def test_delete_post(self, auth_client, test_user):
        """测试删除帖子"""
        # 1. 创建帖子
        self.test_create_post(auth_client)
        post = Post.objects.filter(author__username=test_user.username).first()
        
        # 2. 删除帖子
        url = f'/api/v1/posts/{post.id}/delete/'
        response = auth_client.delete(url)
        
        assert response.status_code == 200
        assert response.json()['code'] == 200
        
        # 3. 验证数据库
        assert not Post.objects.filter(id=post.id).exists()

    def test_toggle_post_like(self, auth_client):
        """测试帖子点赞/取消点赞"""
        self.test_create_post(auth_client)
        post = Post.objects.first()
        
        url = f'/api/v1/posts/{post.id}/like/'
        
        # 1. 点赞
        response = auth_client.post(url)
        assert response.status_code == 200
        assert response.json()['code'] == 200
        # 修正：根据 post/views.py 的实现，返回的字段是 is_liked 而不是 liked
        assert response.json()['data']['is_liked'] is True
        
        post.refresh_from_db()
        # 修正：字段名是 likes_count
        assert post.likes_count == 1
        
        # 2. 取消点赞
        response = auth_client.post(url)
        assert response.status_code == 200
        assert response.json()['data']['is_liked'] is False
        
        post.refresh_from_db()
        assert post.likes_count == 0

    def test_comment_list(self, auth_client):
        """测试获取评论列表"""
        self.test_create_comment(auth_client)
        post = Post.objects.first()
        
        url = f'/api/v1/posts/{post.id}/comments/'
        response = auth_client.get(url)
        
        assert response.status_code == 200
        assert response.json()['code'] == 200
        assert len(response.json()['data']['comments']) > 0

    def test_delete_comment(self, auth_client, test_user):
        """测试删除评论"""
        self.test_create_comment(auth_client)
        comment = Comment.objects.filter(author__username=test_user.username).first()
        
        url = f'/api/v1/comments/{comment.id}/delete/'
        response = auth_client.delete(url)
        
        assert response.status_code == 200
        assert response.json()['code'] == 200
        assert not Comment.objects.filter(id=comment.id).exists()

    def test_toggle_comment_like(self, auth_client):
        """测试评论点赞/取消点赞"""
        self.test_create_comment(auth_client)
        comment = Comment.objects.first()
        
        url = f'/api/v1/comments/{comment.id}/like/'
        
        # 1. 点赞
        response = auth_client.post(url)
        assert response.status_code == 200
        assert response.json()['code'] == 200
        # 修正：根据 post/views.py 的实现，返回的字段是 is_liked 而不是 liked
        assert response.json()['data']['is_liked'] is True
        
        comment.refresh_from_db()
        # 修正：字段名是 likes_count
        assert comment.likes_count == 1
        
        # 2. 取消点赞
        response = auth_client.post(url)
        assert response.status_code == 200
        assert response.json()['data']['is_liked'] is False
        
        comment.refresh_from_db()
        assert comment.likes_count == 0
