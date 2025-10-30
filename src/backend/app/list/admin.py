from django.contrib import admin
from .models import Canteen, Tag, Dish, Rating, Review

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

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def get_pending_tags(self, obj):
        return ", ".join([tag.name for tag in obj.pending_tags.all()])
    get_pending_tags.short_description = 'Pending Tags'
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
    list_display = ['id', 'user', 'dish', 'content_preview', 'likes_count', 'created_at']
    list_filter = ['created_at', 'likes_count']
    search_fields = ['user__username', 'dish__name', 'content']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at', 'likes_count']

    def content_preview(self, obj):
        """显示评论内容的前50个字符"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'
