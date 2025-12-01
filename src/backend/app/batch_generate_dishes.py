"""
批量生成菜品数据 - 高级版
支持自定义生成数量和更多选项
"""
import os
import sys
import django
import random
import argparse
from decimal import Decimal

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Canteen, Dish, Tag


def clear_existing_data(confirm=False):
    """清空现有菜品数据"""
    if not confirm:
        response = input("⚠️  确定要删除所有现有菜品数据吗？(yes/no): ")
        if response.lower() != 'yes':
            print("取消操作")
            return False
    
    print("\n清理现有数据...")
    dish_count = Dish.objects.count()
    Dish.objects.all().delete()
    print(f"✓ 已删除 {dish_count} 道菜品")
    return True


def generate_batch(
    dishes_per_canteen=50,
    min_price=5.0,
    max_price=30.0,
    min_rating=3.5,
    max_rating=5.0,
    clear_data=False
):
    """
    批量生成菜品
    
    参数:
        dishes_per_canteen: 每个餐厅生成的菜品数量
        min_price: 最低价格
        max_price: 最高价格
        min_rating: 最低评分
        max_rating: 最高评分
        clear_data: 是否清空现有数据
    """
    
    if clear_data:
        if not clear_existing_data():
            return
    
    # 导入生成模块
    from generate_dishes import (
        create_tags, generate_dishes_for_canteen,
        CHINESE_DISHES
    )
    
    print("\n" + "="*70)
    print("食堂菜品批量生成器 - 高级模式")
    print("="*70 + "\n")
    
    # 创建标签
    create_tags()
    
    # 获取所有餐厅
    canteens = Canteen.objects.all()
    
    if not canteens.exists():
        print("❌ 错误: 数据库中没有餐厅！")
        return
    
    print(f"配置:")
    print(f"  - 餐厅数量: {canteens.count()}")
    print(f"  - 每个餐厅菜品数: {dishes_per_canteen}")
    print(f"  - 价格范围: ¥{min_price} - ¥{max_price}")
    print(f"  - 评分范围: {min_rating} - {max_rating}")
    print()
    
    # 计算每个类别应该生成多少道菜
    total_categories = len(CHINESE_DISHES)
    dishes_per_category = max(1, dishes_per_canteen // total_categories)
    
    total_dishes = 0
    
    # 为每个餐厅生成菜品
    for i, canteen in enumerate(canteens, 1):
        print(f"\n[{i}/{canteens.count()}] {canteen.name}")
        count = generate_dishes_for_canteen(canteen, dishes_per_category)
        total_dishes += count
    
    # 最终统计
    print("\n" + "="*70)
    print("✅ 生成完成！")
    print("="*70)
    print(f"\n统计信息:")
    print(f"  📍 餐厅总数: {canteens.count()}")
    print(f"  🍽️  菜品总数: {total_dishes}")
    print(f"  🏷️  标签总数: {Tag.objects.count()}")
    print(f"  📊 平均每餐厅: {total_dishes // canteens.count()} 道菜")
    print("\n" + "="*70 + "\n")


def show_statistics():
    """显示当前数据统计"""
    print("\n" + "="*70)
    print("数据库统计")
    print("="*70 + "\n")
    
    canteens = Canteen.objects.all()
    
    print(f"餐厅总数: {canteens.count()}\n")
    
    for canteen in canteens:
        dish_count = canteen.dishes.count()
        avg_price = canteen.dishes.aggregate(
            avg_price=django.db.models.Avg('price')
        )['avg_price'] or 0
        avg_rating = canteen.dishes.aggregate(
            avg_rating=django.db.models.Avg('rating')
        )['avg_rating'] or 0
        
        print(f"{canteen.name}:")
        print(f"  - 菜品数: {dish_count}")
        print(f"  - 平均价格: ¥{avg_price:.2f}")
        print(f"  - 平均评分: {avg_rating:.2f}")
        print()
    
    print(f"总菜品数: {Dish.objects.count()}")
    print(f"总标签数: {Tag.objects.count()}")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='食堂菜品批量生成器')
    parser.add_argument(
        '-n', '--number',
        type=int,
        default=50,
        help='每个餐厅生成的菜品数量 (默认: 50)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='清空现有菜品数据'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='仅显示统计信息'
    )
    parser.add_argument(
        '--min-price',
        type=float,
        default=5.0,
        help='最低价格 (默认: 5.0)'
    )
    parser.add_argument(
        '--max-price',
        type=float,
        default=30.0,
        help='最高价格 (默认: 30.0)'
    )
    
    args = parser.parse_args()
    
    if args.stats:
        show_statistics()
    else:
        generate_batch(
            dishes_per_canteen=args.number,
            min_price=args.min_price,
            max_price=args.max_price,
            clear_data=args.clear
        )
