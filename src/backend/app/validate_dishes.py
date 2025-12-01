"""
验证生成的菜品数据
检查数据完整性和合理性
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Canteen, Dish, Tag, Floor, Window
from django.db.models import Avg, Count, Max, Min


def validate_data():
    """验证数据完整性"""
    print("\n" + "="*70)
    print("菜品数据验证报告")
    print("="*70 + "\n")
    
    # 基础统计
    canteen_count = Canteen.objects.count()
    dish_count = Dish.objects.count()
    tag_count = Tag.objects.count()
    floor_count = Floor.objects.count()
    window_count = Window.objects.count()
    
    if canteen_count == 0:
        print("❌ 错误: 没有餐厅数据！")
        return
    
    if dish_count == 0:
        print("❌ 错误: 没有菜品数据！")
        return
    
    print("📊 基础数据:")
    print(f"  ✓ 餐厅数量: {canteen_count}")
    print(f"  ✓ 菜品总数: {dish_count}")
    print(f"  ✓ 标签总数: {tag_count}")
    print(f"  ✓ 楼层总数: {floor_count}")
    print(f"  ✓ 窗口总数: {window_count}")
    print(f"  ✓ 平均每餐厅: {dish_count / canteen_count:.1f} 道菜")
    if floor_count > 0:
        print(f"  ✓ 平均每餐厅: {floor_count / canteen_count:.1f} 层楼")
    if window_count > 0:
        print(f"  ✓ 平均每餐厅: {window_count / canteen_count:.1f} 个窗口")
    print()
    
    # 价格统计
    price_stats = Dish.objects.aggregate(
        avg_price=Avg('price'),
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    print("💰 价格分析:")
    print(f"  ✓ 平均价格: ¥{price_stats['avg_price']:.2f}")
    print(f"  ✓ 最低价格: ¥{price_stats['min_price']:.2f}")
    print(f"  ✓ 最高价格: ¥{price_stats['max_price']:.2f}")
    print()
    
    # 评分统计
    rating_stats = Dish.objects.aggregate(
        avg_rating=Avg('rating'),
        min_rating=Min('rating'),
        max_rating=Max('rating')
    )
    
    print("⭐ 评分分析:")
    print(f"  ✓ 平均评分: {rating_stats['avg_rating']:.2f}")
    print(f"  ✓ 最低评分: {rating_stats['min_rating']:.2f}")
    print(f"  ✓ 最高评分: {rating_stats['max_rating']:.2f}")
    
    # 评分分布
    rating_ranges = [
        (3.5, 4.0, "3.5-4.0分"),
        (4.0, 4.5, "4.0-4.5分"),
        (4.5, 5.0, "4.5-5.0分")
    ]
    
    print("\n  评分分布:")
    for min_r, max_r, label in rating_ranges:
        count = Dish.objects.filter(rating__gte=min_r, rating__lt=max_r).count()
        percentage = (count / dish_count * 100) if dish_count > 0 else 0
        print(f"    {label}: {count:3d} 道 ({percentage:5.1f}%)")
    print()
    
    # 标签使用情况
    print("🏷️  标签使用情况:")
    
    # 有标签的菜品
    dishes_with_tags = Dish.objects.annotate(
        tag_count=Count('tags')
    ).filter(tag_count__gt=0).count()
    
    print(f"  ✓ 已打标签菜品: {dishes_with_tags}/{dish_count} ({dishes_with_tags/dish_count*100:.1f}%)")
    
    # 有pending tags的菜品
    dishes_with_pending = Dish.objects.annotate(
        pending_count=Count('pending_tags')
    ).filter(pending_count__gt=0).count()
    
    print(f"  ✓ 有待审核标签: {dishes_with_pending}/{dish_count} ({dishes_with_pending/dish_count*100:.1f}%)")
    
    # 最常用的标签
    print("\n  最常用标签 (Top 10):")
    top_tags = Tag.objects.annotate(
        dish_count=Count('dishes')
    ).order_by('-dish_count')[:10]
    
    for i, tag in enumerate(top_tags, 1):
        print(f"    {i:2d}. {tag.name:15s} - {tag.dish_count:3d} 道菜")
    print()
    
    # 每个餐厅的详细情况
    print("📍 各餐厅详情:")
    print()
    
    canteens = Canteen.objects.annotate(
        dish_count=Count('dishes'),
        floor_count=Count('floors'),
        window_count=Count('floors__windows')
    ).order_by('-dish_count')
    
    for canteen in canteens:
        canteen_dishes = canteen.dishes.aggregate(
            avg_price=Avg('price'),
            avg_rating=Avg('rating'),
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        print(f"  {canteen.name}:")
        print(f"    - 楼层数量: {canteen.floor_count}")
        print(f"    - 窗口数量: {canteen.window_count}")
        print(f"    - 菜品数量: {canteen.dish_count}")
        print(f"    - 价格范围: ¥{canteen_dishes['min_price']:.2f} - ¥{canteen_dishes['max_price']:.2f}")
        print(f"    - 平均价格: ¥{canteen_dishes['avg_price']:.2f}")
        print(f"    - 平均评分: {canteen_dishes['avg_rating']:.2f}")
        print()
    
    # 数据完整性检查
    print("🔍 数据完整性检查:")
    
    issues = []
    
    # 检查缺少描述的菜品
    no_desc = Dish.objects.filter(description='').count()
    if no_desc > 0:
        issues.append(f"  ⚠️  {no_desc} 道菜缺少描述")
    
    # 检查价格异常
    price_zero = Dish.objects.filter(price=0).count()
    if price_zero > 0:
        issues.append(f"  ⚠️  {price_zero} 道菜价格为0")
    
    # 检查评分异常
    rating_zero = Dish.objects.filter(rating=0).count()
    if rating_zero > 0:
        issues.append(f"  ⚠️  {rating_zero} 道菜评分为0")
    
    # 检查没有标签的菜品
    no_tags = Dish.objects.annotate(
        tag_count=Count('tags')
    ).filter(tag_count=0).count()
    if no_tags > 0:
        issues.append(f"  ℹ️  {no_tags} 道菜没有标签")
    
    # 检查没有窗口的菜品
    no_window = Dish.objects.filter(window__isnull=True).count()
    if no_window > 0:
        issues.append(f"  ⚠️  {no_window} 道菜没有分配窗口")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("  ✅ 所有数据完整性检查通过！")
    
    print()
    
    # 推荐菜品展示
    print("🌟 推荐菜品 (评分最高的5道):")
    print()
    
    top_dishes = Dish.objects.order_by('-rating', '-view_count')[:5]
    for i, dish in enumerate(top_dishes, 1):
        tags_str = ', '.join([tag.name for tag in dish.tags.all()[:3]])
        print(f"  {i}. {dish.name}")
        print(f"     餐厅: {dish.canteen.name}")
        print(f"     价格: ¥{dish.price}  评分: {dish.rating}  浏览: {dish.view_count}次")
        print(f"     标签: {tags_str}")
        print()
    
    print("="*70)
    print("✅ 验证完成！")
    print("="*70 + "\n")


def show_sample_dishes():
    """展示样本菜品"""
    print("\n" + "="*70)
    print("样本菜品展示")
    print("="*70 + "\n")
    
    # 随机选择5道菜展示
    import random
    
    all_dishes = list(Dish.objects.all())
    if len(all_dishes) == 0:
        print("没有菜品数据")
        return
    
    sample_dishes = random.sample(all_dishes, min(5, len(all_dishes)))
    
    for i, dish in enumerate(sample_dishes, 1):
        print(f"菜品 {i}: {dish.name}")
        print(f"餐厅: {dish.canteen.name}")
        print(f"价格: ¥{dish.price}")
        print(f"评分: {dish.rating}")
        print(f"描述: {dish.description[:100]}...")
        
        tags = list(dish.tags.all())
        if tags:
            tags_str = ', '.join([tag.name for tag in tags])
            print(f"标签: {tags_str}")
        
        pending_tags = list(dish.pending_tags.all())
        if pending_tags:
            pending_str = ', '.join([tag.name for tag in pending_tags])
            print(f"待审核标签: {pending_str}")
        
        print()
    
    print("="*70 + "\n")


if __name__ == '__main__':
    validate_data()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--sample':
        show_sample_dishes()
