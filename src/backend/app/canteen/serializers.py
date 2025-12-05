"""
食堂消费数据序列化器
"""
from rest_framework import serializers
from .models import CanteenConsumption


class CanteenConsumptionSerializer(serializers.ModelSerializer):
    """食堂消费记录序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CanteenConsumption
        fields = [
            'id',
            'username',
            'idserial',
            'total_amount',
            'canteen_count',
            'canteen_data',
            'last_fetched',
            'created'
        ]
        read_only_fields = [
            'id',
            'username',
            'total_amount',
            'canteen_count',
            'canteen_data',
            'last_fetched',
            'created'
        ]


class BindIdserialSerializer(serializers.Serializer):
    """绑定学号序列化器"""
    idserial = serializers.CharField(
        max_length=32,
        required=True,
        help_text='清华大学学号'
    )
    browser_type = serializers.ChoiceField(
        choices=['chrome', 'firefox', 'edge', 'safari'],
        default='chrome',
        required=False,
        help_text='浏览器类型，用于获取cookie'
    )


class RefreshDataSerializer(serializers.Serializer):
    """刷新数据序列化器"""
    servicehall = serializers.CharField(
        max_length=512,
        required=False,
        allow_blank=True,
        help_text='servicehall cookie，若不提供则使用已保存的cookie'
    )
    browser_type = serializers.ChoiceField(
        choices=['chrome', 'firefox', 'edge', 'safari'],
        default='chrome',
        required=False,
        help_text='浏览器类型（当需要重新获取cookie时）'
    )
