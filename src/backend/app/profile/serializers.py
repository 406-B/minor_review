from rest_framework import serializers
from login.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户个人资料序列化器
    """
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'created', 'updated']
        read_only_fields = ['id', 'username', 'created', 'updated']


class UpdateProfileSerializer(serializers.Serializer):
    """
    更新个人资料序列化器
    """
    nickname = serializers.CharField(max_length=255, required=False)
    avatar = serializers.ImageField(required=False)

    def validate_nickname(self, value):
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError("昵称不能为空")
        return value


class UpdatePasswordSerializer(serializers.Serializer):
    """
    修改密码序列化器
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("两次输入的新密码不一致")
        if len(data['new_password']) < 6:
            raise serializers.ValidationError("密码长度不能少于6位")
        return data


class UserStatsSerializer(serializers.Serializer):
    """
    用户统计信息序列化器
    """
    liked_posts_count = serializers.IntegerField(help_text="点赞的帖子数量")
    comments_count = serializers.IntegerField(help_text="评论数量")
    posts_count = serializers.IntegerField(help_text="发布的帖子数量")
    following_count = serializers.IntegerField(help_text="关注的人数量")


class UserCommentSerializer(serializers.Serializer):
    """
    用户评论序列化器（用于个人主页显示）
    """
    id = serializers.IntegerField(help_text="评论ID")
    content = serializers.CharField(help_text="评论内容")
    created_at = serializers.DateTimeField(help_text="评论时间")
    post_id = serializers.IntegerField(help_text="所属帖子ID")
    post_subject = serializers.CharField(help_text="所属帖子标题")
