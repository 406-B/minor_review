from django.contrib import admin
from .models import Post, Comment, Like


class IsRootCommentFilter(admin.SimpleListFilter):
    title = '评论类型'
    parameter_name = 'is_root'
    
    def lookups(self, request, model_admin):
        return (
            ('1', '主评论'),
            ('0', '回复'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(parent__isnull=True)
        elif self.value() == '0':
            return queryset.filter(parent__isnull=False)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'subject', 'dish', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['created_at', 'author', 'dish__canteen']
    search_fields = ['subject', 'content', 'author__username', 'dish__name']
    readonly_fields = ['created_at', 'updated_at', 'likes_count', 'comments_count']
    date_hierarchy = 'created_at'
    raw_id_fields = ['dish']  # 使用原始ID字段以提高性能
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'dish__canteen')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'parent', 'content_preview', 'has_images', 'likes_count', 'created_at']
    list_filter = ['created_at', 'author', 'post', IsRootCommentFilter]
    search_fields = ['content', 'author__username', 'post__subject']
    readonly_fields = ['created_at', 'updated_at', 'likes_count']
    date_hierarchy = 'created_at'
    raw_id_fields = ['post', 'parent']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
    
    def has_images(self, obj):
        return bool(obj.images)
    has_images.boolean = True
    has_images.short_description = '包含图片'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'post', 'parent__author')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'like_type', 'object_id', 'created_at']
    list_filter = ['like_type', 'created_at', 'user']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

