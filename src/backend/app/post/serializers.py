from rest_framework import serializers
from .models import Post, Comment, Like
from login.models import User


class AuthorSerializer(serializers.ModelSerializer):
    """作者信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar']


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author = AuthorSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 
                  'updated_at', 'likes_count', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'likes_count']

    def get_is_liked(self, obj):
        """检查当前用户是否点赞了该评论"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user:
            return Like.objects.filter(
                user=request.user,
                like_type='comment',
                object_id=obj.id
            ).exists()
        return False


class PostSerializer(serializers.ModelSerializer):
    """帖子序列化器（列表显示）"""
    author = AuthorSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'subject', 'created_at', 'updated_at', 
                  'likes_count', 'comments_count', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 
                            'likes_count', 'comments_count']

    def get_is_liked(self, obj):
        """检查当前用户是否点赞了该帖子"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user:
            return Like.objects.filter(
                user=request.user,
                like_type='post',
                object_id=obj.id
            ).exists()
        return False


class PostDetailSerializer(serializers.ModelSerializer):
    """帖子详情序列化器（包含完整内容和评论）"""
    author = AuthorSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'subject', 'content', 'created_at', 'updated_at', 
                  'likes_count', 'comments_count', 'is_liked', 'comments']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 
                            'likes_count', 'comments_count']

    def get_is_liked(self, obj):
        """检查当前用户是否点赞了该帖子"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user:
            return Like.objects.filter(
                user=request.user,
                like_type='post',
                object_id=obj.id
            ).exists()
        return False


class PostSummarySerializer(serializers.ModelSerializer):
    """帖子摘要序列化器（仅显示基本信息，不含作者详情）"""
    class Meta:
        model = Post
        fields = ['id', 'subject', 'created_at', 'likes_count', 'comments_count']
        read_only_fields = ['id', 'created_at', 'likes_count', 'comments_count']


class PostHomeSerializer(serializers.ModelSerializer):
    """论坛主页帖子序列化器（显示标题和内容前30字）"""
    author = AuthorSerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'subject', 'content_preview', 'author', 'created_at', 
                  'updated_at', 'likes_count', 'comments_count', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 
                            'likes_count', 'comments_count']

    def get_content_preview(self, obj):
        """获取内容前30个字符"""
        if len(obj.content) > 30:
            return obj.content[:30] + '...'
        return obj.content

    def get_is_liked(self, obj):
        """检查当前用户是否点赞了该帖子"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user:
            return Like.objects.filter(
                user=request.user,
                like_type='post',
                object_id=obj.id
            ).exists()
        return False


class CreatePostSerializer(serializers.ModelSerializer):
    """创建帖子序列化器"""
    class Meta:
        model = Post
        fields = ['subject', 'content']

    def validate_subject(self, value):
        """验证帖子主题"""
        if not value or not value.strip():
            raise serializers.ValidationError("帖子主题不能为空")
        if len(value) > 200:
            raise serializers.ValidationError("帖子主题不能超过200字符")
        return value

    def validate_content(self, value):
        """验证帖子内容"""
        if not value or not value.strip():
            raise serializers.ValidationError("帖子内容不能为空")
        if len(value) > 5000:
            raise serializers.ValidationError("帖子内容不能超过5000字符")
        return value


class CreateCommentSerializer(serializers.ModelSerializer):
    """创建评论序列化器"""
    class Meta:
        model = Comment
        fields = ['post', 'content']

    def validate_content(self, value):
        """验证评论内容"""
        if not value or not value.strip():
            raise serializers.ValidationError("评论内容不能为空")
        if len(value) > 1000:
            raise serializers.ValidationError("评论内容不能超过1000字符")
        return value

    def validate_post(self, value):
        """验证帖子是否存在"""
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("帖子不存在")
        return value
