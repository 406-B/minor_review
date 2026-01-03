"""
更新MySQL数据库中菜品价格脚本
遍历数据库中的所有菜品，随机更新价格
价格范围: 5元-35元，步长0.5元
"""

import os
import sys
import django
import random
from decimal import Decimal
from pathlib import Path

# 设置 Django 环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Dish

def update_dish_price():
    """
    更新所有菜品的价格
    价格范围: 5元-35元，步长0.5元
    """
    print("\n" + "="*60)
    print("更新MySQL数据库菜品价格脚本")
    print("="*60 + "\n")
    
    # 生成价格列表 [5.0, 5.5, 6.0, ..., 34.5, 35.0]
    # 范围: 5元-35元，步长0.5元
    min_price = 5.0
    max_price = 35.0
    step = 0.5
    
    price_list = []
    current = min_price
    while current <= max_price:
        price_list.append(Decimal(str(current)))
        current += step
    
    print(f"💰 价格范围: {min_price}元 - {max_price}元，步长: {step}元")
    print(f"💰 可选价格数量: {len(price_list)} 个\n")
    
    # 获取所有菜品
    dishes = Dish.objects.all()
    total_count = dishes.count()
    
    if total_count == 0:
        print("❌ 数据库中没有菜品数据！")
        return
    
    print(f"📊 找到 {total_count} 个菜品，开始更新价格...\n")
    
    updated_count = 0
    price_stats = {}  # 统计价格分布
    
    for i, dish in enumerate(dishes, 1):
        # 随机选择一个价格
        old_price = dish.price
        new_price = random.choice(price_list)
        
        # 更新菜品的价格
        dish.price = new_price
        dish.save(update_fields=['price'])
        
        updated_count += 1
        
        # 统计价格分布
        price_key = float(new_price)
        price_stats[price_key] = price_stats.get(price_key, 0) + 1
        
        # 每处理50个菜品打印一次进度
        if i % 50 == 0 or i == total_count:
            progress = (i / total_count) * 100
            print(f"⏳ 进度: {i}/{total_count} ({progress:.1f}%) - "
                  f"最新: {dish.name[:20]}... ¥{old_price} → ¥{new_price}")
    
    print("\n" + "="*60)
    print(f"✅ 更新完成！共更新 {updated_count} 个菜品的价格")
    print(f"💰 价格范围: ¥{min_price} - ¥{max_price}，步长: ¥{step}")
    
    # 显示价格分布统计（显示前10个最常见的价格）
    print("\n📊 价格分布统计 (前10):")
    sorted_prices = sorted(price_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for price, count in sorted_prices:
        percentage = (count / total_count) * 100
        print(f"   ¥{price:.1f}: {count} 个菜品 ({percentage:.1f}%)")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        # 确认操作
        print("⚠️  警告: 此操作将更新数据库中所有菜品的价格！")
        print("📝 价格设置: 5元-35元，步长0.5元")
        confirm = input("确认继续？(yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            update_dish_price()
        else:
            print("\n❌ 操作已取消")
    except KeyboardInterrupt:
        print("\n\n❌ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
