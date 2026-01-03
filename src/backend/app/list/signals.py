"""
Django信号处理 - 自动清除缓存
当数据更新时，自动清除相关缓存
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Canteen, Dish, Floor, Window, Rating, Review
from utils.cache_utils import CacheManager, invalidate_cache
import logging

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Canteen)
def invalidate_canteen_cache_on_change(sender, instance, **kwargs):
    """食堂数据变化时清除缓存"""
    logger.info(f"Invalidating canteen cache for canteen_id={instance.id}")
    CacheManager.invalidate_canteen_cache(instance.id)
    # 也清除食堂列表缓存
    invalidate_cache('canteen_list_*', cache_alias='long_term')


@receiver([post_save, post_delete], sender=Floor)
@receiver([post_save, post_delete], sender=Window)
def invalidate_floor_window_cache_on_change(sender, instance, **kwargs):
    """楼层或窗口数据变化时清除相关食堂缓存"""
    if hasattr(instance, 'canteen'):
        canteen_id = instance.canteen.id
    elif hasattr(instance, 'floor'):
        canteen_id = instance.floor.canteen.id
    else:
        return
    
    logger.info(f"Invalidating floors cache for canteen_id={canteen_id}")
    invalidate_cache(f'canteen_floors:{canteen_id}*', cache_alias='long_term')


@receiver([post_save, post_delete], sender=Dish)
def invalidate_dish_cache_on_change(sender, instance, **kwargs):
    """菜品数据变化时清除缓存"""
    logger.info(f"Invalidating dish cache for dish_id={instance.id}")
    CacheManager.invalidate_dish_cache(instance.id)
    
    # 清除相关食堂的楼层缓存（因为包含菜品信息）
    if instance.canteen_id:
        invalidate_cache(f'canteen_floors:{instance.canteen_id}*', cache_alias='long_term')
    
    # 清除热门菜品缓存
    invalidate_cache('hot_dishes:*', cache_alias='default')


@receiver(post_save, sender=Rating)
def invalidate_rating_cache_on_change(sender, instance, **kwargs):
    """评分变化时清除相关缓存"""
    logger.info(f"Invalidating rating cache for dish_id={instance.dish_id}")
    # 清除菜品详情缓存
    invalidate_cache(f'dish_detail:{instance.dish_id}*', cache_alias='short_term')
    # 清除菜品评分缓存
    invalidate_cache(f'dish_ratings:{instance.dish_id}*', cache_alias='default')
    # 清除热门菜品缓存
    invalidate_cache('hot_dishes:*', cache_alias='default')


@receiver(post_save, sender=Review)
def invalidate_review_cache_on_change(sender, instance, **kwargs):
    """评论变化时清除相关缓存"""
    logger.info(f"Invalidating review cache for dish_id={instance.dish_id}")
    invalidate_cache(f'dish_reviews:{instance.dish_id}*', cache_alias='default')
