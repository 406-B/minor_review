from rest_framework import serializers
from .models import Post, Comment, Like
from login.models import User
from list.models import Dish


class DishSimpleSerializer(serializers.ModelSerializer):
    """菜品简单信息序列化器"""
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)
    
    class Meta:
        model = Dish
        fields = ['id', 'name', 'price', 'image', 'canteen_name']
        read_only_fields = ['id', 'name', 'price', 'image', 'canteen_name']

class AuthorSerializer(serializers.ModelSerializer):
    """作者信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar']


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'images', 'parent',
                  'created_at', 'updated_at', 'likes_count', 'is_liked', 'replies']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'likes_count']

    def get_replies(self, obj):
        """获取回复评论（仅显示直接回复）"""
        if obj.parent is None:  # 只有顶级评论才显示回复
            replies = obj.replies.all().order_by('created_at')
            return CommentReplySerializer(replies, many=True, context=self.context).data
        return []

    def get_is_liked(self, obj):
        """检查当前用户是否点赞了该评论"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                like_type='comment',
                object_id=obj.id
            ).exists()
        return False
    
class CommentReplySerializer(serializers.ModelSerializer):
    """回复评论序列化器（简化版，不包括嵌套回复）"""
    author = AuthorSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'images', 'parent',
                  'created_at', 'updated_at', 'likes_count', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'likes_count']

    def get_is_liked(self, obj):
        """检查当前用户是否点赞了该评论"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                like_type='comment',
                object_id=obj.id
            ).exists()
        return False


class PostSerializer(serializers.ModelSerializer):
    """帖子序列化器（列表显示）"""
    author = AuthorSerializer(read_only=True)
    dish = DishSimpleSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'subject', 'images', 'dish', 'created_at', 'updated_at', 
                  'likes_count', 'comments_count', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 
                            'likes_count', 'comments_count']

    def get_is_liked(self, obj):
        """检查当前用户是否点赞了该帖子"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                like_type='post',
                object_id=obj.id
            ).exists()
        return False


class PostDetailSerializer(serializers.ModelSerializer):
    """帖子详情序列化器（包含完整内容和评论）"""
    author = AuthorSerializer(read_only=True)
    dish = DishSimpleSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'subject', 'content', 'images', 'dish', 'created_at', 'updated_at', 
                  'likes_count', 'comments_count', 'is_liked', 'comments']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 
                            'likes_count', 'comments_count']
    
    def get_comments(self, obj):
        """获取顶级评论（不包括回复）"""
        top_level_comments = obj.comments.filter(parent__isnull=True).order_by('created_at')
        return CommentSerializer(top_level_comments, many=True, context=self.context).data

    def get_is_liked(self, obj):
        """检查当前用户是否点赞了该帖子"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
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
        fields = ['id', 'subject', 'content_preview', 'images', 'author', 'created_at', 
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
        fields = ['subject', 'content', 'images', 'dish']

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
    
    def validate_images(self, value):
        """验证图片列表"""
        if value and len(value) > 9:
            raise serializers.ValidationError("每个帖子最多可上传9张图片")
        return value
    
    def validate_dish(self, value):
        """验证菜品是否存在"""
        if value and not Dish.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("菜品不存在")
        return value


class CreateCommentSerializer(serializers.ModelSerializer):
    """创建评论序列化器"""
    class Meta:
        model = Comment
        fields = ['post', 'content', 'images', 'parent']

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
    
    def validate_parent(self, value):
        """验证父评论"""
        if value:
            # 检查父评论是否存在
            if not Comment.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("父评论不存在")
            # 防止多级回复（只允许回复顶级评论）
            if value.parent is not None:
                raise serializers.ValidationError("只能回复顶级评论")
        return value

    def validate_images(self, value):
        """验证图片列表"""
        if value and len(value) > 9:
            raise serializers.ValidationError("每条评论最多可上传9张图片")
        return value
