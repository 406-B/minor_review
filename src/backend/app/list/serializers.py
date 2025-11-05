from rest_framework import serializers
from .models import Canteen, Tag, Dish

class CanteenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canteen
        fields = '__all__'
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
            'rating', 'view_count', 'created_at', 'updated_at'
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
    """Simplified serializer for list views"""
    tags = TagSerializer(many=True, read_only=True)
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)
    
    class Meta:
        model = Dish
        fields = ['id', 'name', 'price', 'image', 'canteen_name', 'tags', 'rating', 'view_count']