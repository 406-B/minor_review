"""
Django管理命令 - 缓存管理
"""
from django.core.management.base import BaseCommand
from django.core.cache import caches
from utils.cache_utils import CacheManager


class Command(BaseCommand):
    help = '管理Redis缓存'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['clear', 'stats', 'clear_all'],
            help='操作类型：clear清除特定缓存, stats查看统计, clear_all清除所有缓存'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='缓存key模式（用于clear操作）',
            default=None
        )
        parser.add_argument(
            '--alias',
            type=str,
            choices=['default', 'long_term', 'short_term'],
            help='缓存别名',
            default='default'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'stats':
            self.show_stats()
        elif action == 'clear':
            self.clear_cache(options['pattern'], options['alias'])
        elif action == 'clear_all':
            self.clear_all_caches()

    def show_stats(self):
        """显示缓存统计信息"""
        self.stdout.write(self.style.SUCCESS('=== Redis 缓存统计 ==='))
        stats = CacheManager.get_cache_stats()
        
        for alias, data in stats.items():
            self.stdout.write(f"\n{alias}:")
            if 'error' in data:
                self.stdout.write(self.style.ERROR(f"  错误: {data['error']}"))
            else:
                self.stdout.write(f"  命中次数: {data.get('hits', 0)}")
                self.stdout.write(f"  未命中次数: {data.get('misses', 0)}")
                self.stdout.write(f"  缓存键数量: {data.get('keys', 0)}")
                
                hits = data.get('hits', 0)
                misses = data.get('misses', 0)
                total = hits + misses
                if total > 0:
                    hit_rate = (hits / total) * 100
                    self.stdout.write(f"  命中率: {hit_rate:.2f}%")

    def clear_cache(self, pattern, alias):
        """清除指定模式的缓存"""
        if not pattern:
            self.stdout.write(self.style.ERROR('请使用 --pattern 指定要清除的缓存模式'))
            return
        
        try:
            redis_cache = caches[alias]
            redis_cache.delete_pattern(pattern)
            self.stdout.write(self.style.SUCCESS(f'已清除缓存: {pattern} (alias={alias})'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'清除缓存失败: {e}'))

    def clear_all_caches(self):
        """清除所有缓存"""
        self.stdout.write(self.style.WARNING('警告：即将清除所有缓存！'))
        confirm = input('确认继续？(yes/no): ')
        
        if confirm.lower() != 'yes':
            self.stdout.write('已取消操作')
            return
        
        for alias in ['default', 'long_term', 'short_term']:
            try:
                redis_cache = caches[alias]
                redis_cache.clear()
                self.stdout.write(self.style.SUCCESS(f'已清除 {alias} 缓存'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'清除 {alias} 缓存失败: {e}'))
