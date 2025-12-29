"""
Redis缓存工具类
提供统一的缓存接口和装饰器
"""
from functools import wraps
from django.core.cache import caches
import hashlib
import logging

logger = logging.getLogger(__name__)


def get_cache_key(*args, prefix='', **kwargs):
    """
    生成缓存key
    :param args: 位置参数
    :param prefix: key前缀
    :param kwargs: 关键字参数
    :return: 缓存key
    """
    key_parts = [prefix] if prefix else []
    
    # 添加位置参数
    for arg in args:
        if arg is not None:
            key_parts.append(str(arg))
    
    # 添加关键字参数（排序保证一致性）
    for k in sorted(kwargs.keys()):
        v = kwargs[k]
        if v is not None:
            key_parts.append(f"{k}={v}")
    
    key_str = ':'.join(key_parts)
    
    # 如果key太长，使用hash
    if len(key_str) > 200:
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:hash:{key_hash}"
    
    return key_str


def cache_result(timeout=300, cache_alias='default', key_prefix=''):
    """
    缓存函数结果的装饰器
    
    使用示例：
    @cache_result(timeout=600, key_prefix='canteen_floors')
    def get_canteen_floors(canteen_id):
        # 查询数据库
        return floors
    
    :param timeout: 缓存时间（秒）
    :param cache_alias: 缓存别名 ('default', 'long_term', 'short_term')
    :param key_prefix: 缓存key前缀
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存key
            cache_key = get_cache_key(*args, prefix=key_prefix or func.__name__, **kwargs)
            
            # 尝试从缓存获取
            redis_cache = caches[cache_alias]
            cached_result = redis_cache.get(cache_key)
            
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result
            
            # 缓存未命中，执行函数
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            
            # 保存到缓存
            try:
                redis_cache.set(cache_key, result, timeout)
            except Exception as e:
                logger.error(f"Cache set error: {e}")
            
            return result
        return wrapper
    return decorator


def invalidate_cache(key_pattern=None, cache_alias='default'):
    """
    清除缓存
    :param key_pattern: 缓存key模式（支持通配符）
    :param cache_alias: 缓存别名
    """
    try:
        redis_cache = caches[cache_alias]
        if key_pattern:
            # 删除匹配的keys
            redis_cache.delete_pattern(key_pattern)
            logger.info(f"Cache invalidated: {key_pattern}")
        else:
            # 清空所有缓存
            redis_cache.clear()
            logger.info(f"All cache cleared in {cache_alias}")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")


class CacheManager:
    """缓存管理类"""
    
    @staticmethod
    def get_or_set(key, callback, timeout=300, cache_alias='default'):
        """
        获取缓存，如果不存在则调用callback并缓存结果
        
        使用示例：
        canteens = CacheManager.get_or_set(
            'canteen_list',
            lambda: Canteen.objects.all(),
            timeout=3600,
            cache_alias='long_term'
        )
        """
        redis_cache = caches[cache_alias]
        result = redis_cache.get(key)
        
        if result is None:
            result = callback()
            try:
                redis_cache.set(key, result, timeout)
            except Exception as e:
                logger.error(f"Cache set error: {e}")
        
        return result
    
    @staticmethod
    def invalidate_dish_cache(dish_id=None):
        """清除菜品相关缓存"""
        if dish_id:
            patterns = [
                f"*dish_detail:{dish_id}*",
                f"*dish_reviews:{dish_id}*",
                f"*dish_ratings:{dish_id}*",
            ]
        else:
            patterns = ["*dish*"]
        
        for pattern in patterns:
            invalidate_cache(pattern)
    
    @staticmethod
    def invalidate_canteen_cache(canteen_id=None):
        """清除食堂相关缓存"""
        if canteen_id:
            patterns = [
                f"*canteen_floors:{canteen_id}*",
                f"*canteen_detail:{canteen_id}*",
            ]
        else:
            patterns = ["*canteen*"]
        
        for pattern in patterns:
            invalidate_cache(pattern)
    
    @staticmethod
    def get_cache_stats():
        """获取缓存统计信息"""
        stats = {}
        for alias in ['default', 'long_term', 'short_term']:
            try:
                redis_cache = caches[alias]
                # 这需要redis客户端支持
                info = redis_cache.client.get_client().info('stats')
                stats[alias] = {
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                    'keys': redis_cache.client.get_client().dbsize(),
                }
            except Exception as e:
                logger.error(f"Get cache stats error for {alias}: {e}")
                stats[alias] = {'error': str(e)}
        
        return stats
