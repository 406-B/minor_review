from django.contrib import admin
from .models import Canteen, Tag, Dish

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
    list_display=['name', 'description', 'price', 'image', 'canteen', 'rating', 'view_count', 'get_tags', 'created_at', 'updated_at']
    list_filter=['canteen', 'tags', 'created_at', 'updated_at']
    search_fields = ['name', 'description', 'canteen__name', 'tags__name']
    ordering = ['-rating', 'name', 'canteen__name']
    list_per_page = 100
    filter_horizontal = ['tags']
    
    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'
    