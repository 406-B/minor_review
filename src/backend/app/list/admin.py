from django.contrib import admin
from .models import Canteen, Tag, Dish, Rating, Review, Floor, Window
# 注册 Floor
@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'canteen', 'order']
    list_filter = ['canteen']
    search_fields = ['name', 'canteen__name']
    ordering = ['canteen', 'order', 'id']
    list_per_page = 50

# 注册 Window
@admin.register(Window)
class WindowAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'floor', 'order']
    list_filter = ['floor']
    search_fields = ['name', 'floor__name', 'floor__canteen__name']
    ordering = ['floor', 'order', 'id']
    list_per_page = 50

# Register your models here.
@admin.register(Canteen)
class CanteenAdmin(admin.ModelAdmin):
    list_display=['name', 'created_at', 'updated_at']
    list_filter=['created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['name']
    list_per_page = 20
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display=['name', 'created_at', 'updated_at']
    list_filter=['created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['name']
    list_per_page = 100
@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'price', 'image', 'canteen', 'rating', 'view_count', 'get_tags', 'get_pending_tags', 'created_at', 'updated_at']
    list_filter=['canteen', 'tags', 'created_at', 'updated_at']
    search_fields = ['name', 'description', 'canteen__name', 'tags__name']
    ordering = ['-rating', 'name', 'canteen__name']
    list_per_page = 100
    filter_horizontal = ['tags', 'pending_tags']
    actions = ['approve_pending_tags', 'reject_pending_tags']

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def get_pending_tags(self, obj):
        return ", ".join([tag.name for tag in obj.pending_tags.all()])
    get_pending_tags.short_description = 'Pending Tags'

    def approve_pending_tags(self, request, queryset):
        """批量批准待审核标签"""
        total_approved = 0
        for dish in queryset:
            for tag in dish.pending_tags.all():
                if tag not in dish.tags.all():
                    dish.tags.add(tag)
                    total_approved += 1
            dish.pending_tags.clear()
        self.message_user(request, f'成功批准 {total_approved} 个标签')
    approve_pending_tags.short_description = '批准所有待审核标签'

    def reject_pending_tags(self, request, queryset):
        """批量拒绝待审核标签"""
        total_rejected = 0
        for dish in queryset:
            total_rejected += dish.pending_tags.count()
            dish.pending_tags.clear()
        self.message_user(request, f'成功拒绝 {total_rejected} 个标签')
    reject_pending_tags.short_description = '拒绝所有待审核标签'
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'dish', 'score', 'created_at']
    list_filter = ['created_at', 'score']
    search_fields = ['user__username', 'dish__name']
    ordering = ['-created_at']
    list_per_page = 100
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'dish', 'status', 'content_preview', 'likes_count', 'created_at', 'audited_at']
    list_filter = ['created_at', 'likes_count', 'status']
    search_fields = ['user__username', 'dish__name', 'content']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at', 'likes_count', 'audited_at']
    actions = ['approve_reviews', 'reject_reviews']

    def content_preview(self, obj):
        """显示评论内容的前50个字符"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'

    def approve_reviews(self, request, queryset):
        """批量批准评论"""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='approved',
            audited_at=timezone.now(),
            audit_reason=''
        )
        self.message_user(request, f'成功批准 {updated} 个评论')
    approve_reviews.short_description = '批准选中的评论'

    def reject_reviews(self, request, queryset):
        """批量拒绝评论"""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='rejected',
            audited_at=timezone.now(),
            audit_reason='管理员批量拒绝'
        )
        self.message_user(request, f'成功拒绝 {updated} 个评论')
    reject_reviews.short_description = '拒绝选中的评论'
