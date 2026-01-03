"""
更新MySQL数据库中菜品评分人数脚本
遍历数据库中的所有菜品，将评分人数(rating_count)在0-1500区间内随机更新
适用于服务器上的MySQL数据库
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

def update_rating_count():
    """
    更新所有菜品的评分人数
    将评分人数随机设置在0-1500之间
    """
    print("\n" + "="*60)
    print("更新MySQL数据库菜品评分人数脚本")
    print("="*60 + "\n")
    
    # 获取所有菜品
    dishes = Dish.objects.all()
    total_count = dishes.count()
    
    if total_count == 0:
        print("❌ 数据库中没有菜品数据！")
        return
    
    print(f"📊 找到 {total_count} 个菜品，开始更新评分人数...\n")
    
    updated_count = 0
    
    for i, dish in enumerate(dishes, 1):
        # 随机生成0-1500之间的评分人数
        old_rating_count = dish.rating_count
        new_rating_count = random.randint(0, 1500)
        
        # 更新菜品的评分人数
        dish.rating_count = new_rating_count
        dish.save(update_fields=['rating_count'])
        
        updated_count += 1
        
        # 每处理50个菜品打印一次进度
        if i % 50 == 0 or i == total_count:
            progress = (i / total_count) * 100
            print(f"⏳ 进度: {i}/{total_count} ({progress:.1f}%) - "
                  f"最新: {dish.name[:20]}... {old_rating_count} → {new_rating_count}")
    
    print("\n" + "="*60)
    print(f"✅ 更新完成！共更新 {updated_count} 个菜品的评分人数")
    print(f"📈 评分人数范围: 0-1500")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        # 确认操作
        print("⚠️  警告: 此操作将更新数据库中所有菜品的评分人数！")
        confirm = input("确认继续？(yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            update_rating_count()
        else:
            print("\n❌ 操作已取消")
    except KeyboardInterrupt:
        print("\n\n❌ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
