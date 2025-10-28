from rest_framework import serializers
from .models import Canteen, Tag, Dish

class CanteenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canteen
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class TagSerializer(serializers.ModelSerializer):
    dish_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'dish_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_dish_count(self, obj):
        """Return the number of dishes with this tag"""
        return obj.dishes.count()

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
    
    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data
        
        user = request.user
        
        # 如果用户试图修改标签
        if 'tags' in data:
            # 管理员可以直接修改
            if user.is_staff or user.is_superuser:
                # 允许修改，什么都不做
                pass
            else:
                # 普通用户：将标签移到 pending_tags
                data['pending_tags'] = data.pop('tags')
        
        return data
        
class DishListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    tags = TagSerializer(many=True, read_only=True)
    canteen_name = serializers.CharField(source='canteen.name', read_only=True)
    
    class Meta:
        model = Dish
        fields = ['id', 'name', 'price', 'image', 'canteen_name', 'tags', 'rating', 'view_count']