from django.contrib import admin
from .models import Post, Comment, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'subject', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['subject', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'likes_count', 'comments_count']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'content_preview', 'likes_count', 'created_at']
    list_filter = ['created_at', 'author', 'post']
    search_fields = ['content', 'author__username', 'post__content']
    readonly_fields = ['created_at', 'updated_at', 'likes_count']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'like_type', 'object_id', 'created_at']
    list_filter = ['like_type', 'created_at', 'user']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

