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
    list_display = ['id', 'author', 'subject', 'status', 'dish', 'likes_count', 'comments_count', 'created_at', 'audited_at']
    list_filter = ['created_at', 'author', 'dish__canteen', 'status']
    search_fields = ['subject', 'content', 'author__username', 'dish__name']
    readonly_fields = ['created_at', 'updated_at', 'likes_count', 'comments_count', 'audited_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['dish']  # 使用原始ID字段以提高性能
    actions = ['approve_posts', 'reject_posts']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'dish__canteen')

    def approve_posts(self, request, queryset):
        """批量批准帖子"""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='approved',
            audited_at=timezone.now(),
            audit_reason=''
        )
        self.message_user(request, f'成功批准 {updated} 个帖子')
    approve_posts.short_description = '批准选中的帖子'

    def reject_posts(self, request, queryset):
        """批量拒绝帖子"""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='rejected',
            audited_at=timezone.now(),
            audit_reason='管理员批量拒绝'
        )
        self.message_user(request, f'成功拒绝 {updated} 个帖子')
    reject_posts.short_description = '拒绝选中的帖子'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'status', 'parent', 'content_preview', 'has_images', 'likes_count', 'created_at', 'audited_at']
    list_filter = ['created_at', 'author', 'post', 'status', IsRootCommentFilter]
    search_fields = ['content', 'author__username', 'post__subject']
    readonly_fields = ['created_at', 'updated_at', 'likes_count', 'audited_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['post', 'parent']
    actions = ['approve_comments', 'reject_comments']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'

    def has_images(self, obj):
        return bool(obj.images)
    has_images.boolean = True
    has_images.short_description = '包含图片'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'post', 'parent__author')

    def approve_comments(self, request, queryset):
        """批量批准评论"""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='approved',
            audited_at=timezone.now(),
            audit_reason=''
        )
        self.message_user(request, f'成功批准 {updated} 个评论')
    approve_comments.short_description = '批准选中的评论'

    def reject_comments(self, request, queryset):
        """批量拒绝评论"""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='rejected',
            audited_at=timezone.now(),
            audit_reason='管理员批量拒绝'
        )
        self.message_user(request, f'成功拒绝 {updated} 个评论')
    reject_comments.short_description = '拒绝选中的评论'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'like_type', 'object_id', 'created_at']
    list_filter = ['like_type', 'created_at', 'user']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

