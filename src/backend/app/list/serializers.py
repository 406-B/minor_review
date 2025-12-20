from rest_framework import serializers
from .models import Canteen, Tag, Dish, Rating, Review, Floor, Window, UserDishHistory
from login.models import User as LoginUser
class WindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Window
        fields = ['id', 'name', 'order']

class FloorSerializer(serializers.ModelSerializer):
    windows = serializers.SerializerMethodField()
    class Meta:
        model = Floor
        fields = ['id', 'name', 'order', 'windows']
    def get_windows(self, obj):
        windows = obj.windows.all()
        return WindowWithDishesSerializer(windows, many=True).data

class WindowWithDishesSerializer(serializers.ModelSerializer):
    dishes = serializers.SerializerMethodField()
    class Meta:
        model = Window
        fields = ['id', 'name', 'order', 'dishes']
    def get_dishes(self, obj):
        dishes = obj.dishes.all()
        return DishListSerializer(dishes, many=True).data

class CanteenSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True, required=False, help_text="距离（米）")

    class Meta:
        model = Canteen
        fields = ['id', 'name', 'latitude', 'longitude', 'address', 'distance', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_name(self, value):
        """验证食堂名称不为空"""
        if not value or not value.strip():
            raise serializers.ValidationError("食堂名称不能为空")
        return value.strip()

class TagSerializer(serializers.ModelSerializer):
    dish_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'dish_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_dish_count(self, obj):
        """Return the number of dishes with this tag"""
        return obj.dishes.count()

    def validate_name(self, value):
        """验证标签名称不为空且长度符合要求"""
        if not value or not value.strip():
            raise serializers.ValidationError("标签名称不能为空")
        value = value.strip()
        if len(value) > 30:
            raise serializers.ValidationError("标签名称不能超过30个字符")
        return value

class DishSerializer(serializers.ModelSerializer):
    window = WindowSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )
    pending_tags = TagSerializer(many=True, read_only=True)
    pending_tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='pending_tags',
        write_only=True,
        required=False
    )
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)
    has_pending_tags = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = [
            'id', 'name', 'description', 'price', 'image',
            'canteen', 'canteen_name', 'tags', 'tag_ids',
            'pending_tags', 'pending_tag_ids', 'has_pending_tags',
            'rating', 'view_count', 'created_at', 'updated_at',
            'window'
        ]
        read_only_fields = ['created_at', 'updated_at', 'view_count', 'rating']

    def get_has_pending_tags(self, obj):
        """Check if there are pending tags waiting for approval"""
        return obj.pending_tags.exists()

    def validate_name(self, value):
        """验证菜品名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("菜品名称不能为空")
        return value.strip()

    def validate_price(self, value):
        """验证价格非负"""
        if value < 0:
            raise serializers.ValidationError("价格不能为负数")
        return value

class DishListSerializer(serializers.ModelSerializer):
    window = WindowSerializer(read_only=True)
    """Simplified serializer for list views"""
    tags = TagSerializer(many=True, read_only=True)
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)

    class Meta:
        model = Dish
        fields = ['id', 'name', 'price', 'image', 'canteen_name', 'tags', 'rating', 'view_count', 'window']

class RatingSerializer(serializers.ModelSerializer):
    """评分序列化器"""
    username = serializers.CharField(source='user.username', read_only=True, help_text="用户账号名")
    nickname = serializers.CharField(source='user.nickname', read_only=True, help_text="用户昵称")
    dish_name = serializers.CharField(source='dish.name', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'username', 'nickname', 'dish', 'dish_name', 'score', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate_score(self, value):
        """验证评分范围"""
        if value < 1.0 or value > 5.0:
            raise serializers.ValidationError("评分必须在 1.0-5.0 之间")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    username = serializers.CharField(source='user.username', read_only=True, help_text="用户账号名")
    # 兼容 Django AuthUser 无 nickname 字段的情况：从 login.User 表按 username 取昵称
    nickname = serializers.SerializerMethodField(help_text="用户昵称")
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    user_rating = serializers.SerializerMethodField()
    published_score = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    # 显式声明只读外键，避免创建时要求客户端提交
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    dish = serializers.PrimaryKeyRelatedField(read_only=True)
    rating = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'username', 'nickname', 'dish', 'dish_name',
            'content', 'images', 'rating', 'user_rating', 'published_score',
            'likes_count', 'created_at', 'updated_at'
        ]
    # dish 与 rating 在视图中通过上下文注入，不要求客户端提交
    read_only_fields = ['user', 'dish', 'rating', 'likes_count', 'created_at', 'updated_at']

    def get_user_rating(self, obj):
        """显示评论发布时的评分快照，不随后续评分变化"""
        if obj.published_score is not None:
            return obj.published_score
        # 兼容旧数据：若无快照但有关联评分，则暂时显示关联评分
        if obj.rating:
            return obj.rating.score
        return None

    def get_nickname(self, obj):
        # 优先尝试从关联用户对象上获取（若使用了自定义用户模型并包含 nickname）
        nick = getattr(obj.user, 'nickname', None)
        if nick:
            return nick
        # 回退到 login.User 表通过 username 查询
        try:
            return LoginUser.objects.filter(username=obj.user.username).values_list('nickname', flat=True).first() or obj.user.username
        except Exception:
            return obj.user.username

    def validate_content(self, value):
        """验证评论内容"""
        if not value or not value.strip():
            raise serializers.ValidationError("评论内容不能为空")
        if len(value.strip()) < 5:
            raise serializers.ValidationError("评论内容至少5个字符")
        if len(value) > 1000:
            raise serializers.ValidationError("评论内容不能超过1000个字符")
        return value.strip()

    def validate_images(self, value):
        """验证图片列表"""
        if not isinstance(value, list):
            raise serializers.ValidationError("图片必须是列表格式")
        if len(value) > 9:
            raise serializers.ValidationError("最多上传9张图片")
        return value


class ReviewListSerializer(serializers.ModelSerializer):
    """评论列表序列化器（简化版）"""
    username = serializers.CharField(source='user.username', read_only=True, help_text="用户账号名")
    # 同上，提供 nickname 的回退策略
    nickname = serializers.SerializerMethodField(help_text="用户昵称")
    user_rating = serializers.SerializerMethodField()
    published_score = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'username', 'nickname', 'content', 'images',
            'user_rating', 'published_score', 'likes_count', 'created_at'
        ]

    def get_user_rating(self, obj):
        # 优先评论发布时的评分快照
        if obj.published_score is not None:
            return obj.published_score
        # 兼容旧数据：若无快照但有关联评分，则暂时显示关联评分
        if obj.rating:
            return obj.rating.score
        return None

    def get_nickname(self, obj):
        nick = getattr(obj.user, 'nickname', None)
        if nick:
            return nick
        try:
            return LoginUser.objects.filter(username=obj.user.username).values_list('nickname', flat=True).first() or obj.user.username
        except Exception:
            return obj.user.username


class UserDishHistorySerializer(serializers.ModelSerializer):
    """用户菜品历史序列化器"""
    username = serializers.CharField(source='user.username', read_only=True, help_text="用户账号名")
    nickname = serializers.CharField(source='user.nickname', read_only=True, help_text="用户昵称")
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    dish_image = serializers.SerializerMethodField()
    canteen_name = serializers.CharField(source='dish.canteen.name', read_only=True)
    level = serializers.CharField(read_only=True)
    level_display = serializers.CharField(read_only=True)
    level_progress = serializers.SerializerMethodField()

    class Meta:
        model = UserDishHistory
        fields = [
            'id', 'user', 'username', 'nickname', 'dish', 'dish_name', 'dish_image', 'canteen_name',
            'count', 'level', 'level_display', 'level_progress',
            'first_tried_at', 'last_tried_at'
        ]
        read_only_fields = ['user', 'count', 'first_tried_at', 'last_tried_at']

    def get_level_progress(self, obj):
        """获取级别进度信息"""
        return obj.level_progress

    def get_dish_image(self, obj):
        """安全返回菜品图片URL，避免空文件或缺失文件导致异常"""
        try:
            image = getattr(obj.dish, 'image', None)
            if not image:
                return None
            return image.url
        except Exception:
            return None


class UserDishHistoryListSerializer(serializers.ModelSerializer):
    """用户菜品历史列表序列化器（简化版）"""
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    dish_image = serializers.SerializerMethodField()
    level_display = serializers.CharField(read_only=True)

    class Meta:
        model = UserDishHistory
        fields = [
            'id', 'dish', 'dish_name', 'dish_image',
            'count', 'level_display', 'last_tried_at'
        ]

    def get_dish_image(self, obj):
        try:
            image = getattr(obj.dish, 'image', None)
            if not image:
                return None
            return image.url
        except Exception:
            return None
