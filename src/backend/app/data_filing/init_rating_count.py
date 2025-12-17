"""
初始化菜品评分人数脚本
遍历数据库中的所有菜品，将评分人数(rating_count)在0-200区间内随机初始化
"""

import os
import sys
import django
import random
from pathlib import Path

# 设置 Django 环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Dish

def init_rating_count():
    """
    初始化所有菜品的评分人数
    将评分人数随机设置在0-200之间
    """
    print("\n" + "="*60)
    print("初始化菜品评分人数脚本")
    print("="*60 + "\n")
    
    # 获取所有菜品
    dishes = Dish.objects.all()
    total_count = dishes.count()
    
    if total_count == 0:
        print("数据库中没有菜品数据！")
        return
    
    print(f"找到 {total_count} 个菜品，开始初始化评分人数...\n")
    
    updated_count = 0
    
    for i, dish in enumerate(dishes, 1):
        # 随机生成0-200之间的评分人数
        rating_count = random.randint(0, 200)
        
        # 更新菜品的评分人数
        dish.rating_count = rating_count
        dish.save(update_fields=['rating_count'])
        
        updated_count += 1
        
        # 每10个菜品输出一次进度
        if i % 10 == 0 or i == total_count:
            print(f"进度: {i}/{total_count} ({(i/total_count*100):.1f}%) - "
                  f"最新: {dish.name} -> {rating_count}人评分")
    
    print("\n" + "="*60)
    print(f"初始化完成！共更新 {updated_count} 个菜品的评分人数")
    print("="*60 + "\n")
    
    # 统计信息
    print("统计信息:")
    print(f"  - 总菜品数: {total_count}")
    print(f"  - 平均评分人数: {Dish.objects.all().aggregate(avg=models.Avg('rating_count'))['avg']:.1f}")
    print(f"  - 最高评分人数: {Dish.objects.all().aggregate(max=models.Max('rating_count'))['max']}")
    print(f"  - 最低评分人数: {Dish.objects.all().aggregate(min=models.Min('rating_count'))['min']}")
    
    # 显示评分人数分布
    print("\n评分人数分布:")
    ranges = [
        (0, 50, "0-50人"),
        (51, 100, "51-100人"),
        (101, 150, "101-150人"),
        (151, 200, "151-200人"),
    ]
    
    for min_val, max_val, label in ranges:
        count = Dish.objects.filter(
            rating_count__gte=min_val,
            rating_count__lte=max_val
        ).count()
        percentage = (count / total_count * 100) if total_count > 0 else 0
        print(f"  - {label}: {count} 个 ({percentage:.1f}%)")


if __name__ == '__main__':
    from django.db import models
    
    # 确认操作
    print("此脚本将初始化所有菜品的评分人数(rating_count)字段")
    print("评分人数将在 0-200 区间内随机生成")
    
    response = input("\n是否继续? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        init_rating_count()
    else:
        print("操作已取消")
