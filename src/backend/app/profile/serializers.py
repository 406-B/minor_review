from rest_framework import serializers
from login.models import User
from list.models import Tag


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户个人资料序列化器
    """
    avatar = serializers.ImageField(required=False)
    preference_tags = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'preference_tags', 'created', 'updated']
        read_only_fields = ['id', 'username', 'created', 'updated']

    def get_preference_tags(self, obj):
        """获取用户偏好标签"""
        from list.serializers import TagSerializer
        return TagSerializer(obj.preference_tags.all(), many=True).data


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


# ==================== 审核相关序列化器 ====================

class PendingContentSerializer(serializers.Serializer):
    """
    待审核内容序列化器
    """
    id = serializers.IntegerField(help_text="内容ID")
    type = serializers.CharField(help_text="内容类型")
    title = serializers.CharField(help_text="标题")
    content = serializers.CharField(help_text="内容")
    author = serializers.CharField(help_text="作者")
    created_at = serializers.DateTimeField(help_text="创建时间")
    images = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="图片列表"
    )


class AuditActionSerializer(serializers.Serializer):
    """
    审核操作序列化器
    """
    action = serializers.ChoiceField(
        choices=['approve', 'reject'],
        help_text="审核操作：approve(通过) 或 reject(拒绝)"
    )
    reason = serializers.CharField(
        max_length=100,
        required=False,
        help_text="拒绝原因（当action为reject时必填）"
    )

    def validate(self, data):
        if data['action'] == 'reject' and not data.get('reason'):
            raise serializers.ValidationError("拒绝审核时必须提供原因")
        return data


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


class UserPreferenceTagsSerializer(serializers.Serializer):
    """
    用户偏好标签序列化器（用于设置偏好标签）
    """
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="标签ID列表"
    )

    def validate_tag_ids(self, value):
        """验证标签ID是否存在"""
        if not value:
            raise serializers.ValidationError("至少选择一个标签")

        existing_tags = Tag.objects.filter(id__in=value).count()
        if existing_tags != len(value):
            raise serializers.ValidationError("部分标签ID不存在")

        return value


class CheckInDishSerializer(serializers.Serializer):
    """
    打卡菜品序列化器（用于美食日历）
    """
    id = serializers.IntegerField(help_text="菜品ID")
    name = serializers.CharField(help_text="菜品名称")
    image = serializers.SerializerMethodField(help_text="菜品图片URL")
    canteen_name = serializers.CharField(help_text="所属食堂名称")
    window_name = serializers.CharField(help_text="所属窗口名称", allow_null=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, help_text="菜品价格")
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, help_text="菜品评分")
    check_in_time = serializers.DateTimeField(help_text="打卡时间")
    check_in_count = serializers.IntegerField(help_text="该菜品累计打卡次数")
    total_consumption = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="该菜品累计消费金额")
    achievement_tier = serializers.CharField(help_text="成就等级")
    tags = serializers.SerializerMethodField(help_text="菜品标签数组")

    def get_image(self, obj):
        """获取菜品图片URL"""
        if obj.get('dish') and obj['dish'].image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj['dish'].image.url)
            return obj['dish'].image.url
        return None

    def get_tags(self, obj):
        """获取菜品标签"""
        from list.serializers import TagSerializer
        dish = obj.get('dish')
        if dish and hasattr(dish, 'tags'):
            return TagSerializer(dish.tags.all(), many=True).data
        return []


class CheckInDateSerializer(serializers.Serializer):
    """
    打卡日期序列化器（用于美食日历）
    """
    date = serializers.DateField(help_text="日期 (YYYY-MM-DD)")
    dishes = CheckInDishSerializer(many=True, help_text="当天打卡的菜品列表")


class CheckInHistorySummarySerializer(serializers.Serializer):
    """
    打卡历史统计摘要序列化器
    """
    total_check_ins = serializers.IntegerField(help_text="总打卡次数")
    total_dishes = serializers.IntegerField(help_text="不同菜品数量")
    total_consumption = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="总消费金额")
    most_frequent_dish = serializers.DictField(help_text="最常打卡的菜品", allow_null=True)


# ==================== 审核相关序列化器 ====================

class PendingContentSerializer(serializers.Serializer):
    """
    待审核内容序列化器
    """
    id = serializers.IntegerField(help_text="内容ID")
    type = serializers.CharField(help_text="内容类型")
    title = serializers.CharField(help_text="标题")
    content = serializers.CharField(help_text="内容")
    author = serializers.CharField(help_text="作者")
    created_at = serializers.DateTimeField(help_text="创建时间")
    images = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="图片列表"
    )


class AuditActionSerializer(serializers.Serializer):
    """
    审核操作序列化器
    """
    action = serializers.ChoiceField(
        choices=['approve', 'reject'],
        help_text="审核操作：approve(通过) 或 reject(拒绝)"
    )
    reason = serializers.CharField(
        max_length=100,
        required=False,
        help_text="拒绝原因（当action为reject时必填）"
    )

    def validate(self, data):
        if data['action'] == 'reject' and not data.get('reason'):
            raise serializers.ValidationError("拒绝审核时必须提供原因")
        return data
