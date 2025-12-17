"""
食堂消费数据后台管理
"""
from django.contrib import admin
from .models import CanteenConsumption


@admin.register(CanteenConsumption)
class CanteenConsumptionAdmin(admin.ModelAdmin):
    """食堂消费记录管理"""
    list_display = [
        'id',
        'user',
        'idserial',
        'total_amount',
        'canteen_count',
        'last_fetched',
        'created'
    ]
    list_filter = ['last_fetched', 'created']
    search_fields = ['user__username', 'idserial']
    readonly_fields = [
        'last_fetched',
        'created',
        'canteen_data_display'
    ]
    fieldsets = (
        ('用户信息', {
            'fields': ('user', 'idserial')
        }),
        ('消费统计', {
            'fields': ('total_amount', 'canteen_count', 'canteen_data_display')
        }),
        ('认证信息', {
            'fields': ('servicehall_cookie',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('last_fetched', 'created')
        }),
    )
    
    def canteen_data_display(self, obj):
        """格式化显示食堂消费详情"""
        if not obj.canteen_data:
            return "无数据"
        
        lines = []
        for canteen, amount in obj.canteen_data.items():
            lines.append(f"{canteen}: ¥{amount}")
        
        return "\n".join(lines)
    
    canteen_data_display.short_description = "食堂消费详情"
