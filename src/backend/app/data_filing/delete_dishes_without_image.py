"""
删除MySQL数据库中没有图片的菜品脚本
删除list_dish表中image列为空的菜品，并自动处理所有相关的外键引用

涉及的关联表和外键关系：
1. list_rating (CASCADE) - 会自动删除
2. list_review (CASCADE) - 会自动删除
3. list_userdishhistory (CASCADE) - 会自动删除
4. list_dishcheckinrecord (CASCADE) - 会自动删除
5. post_post (SET_NULL) - 会自动设置为NULL
6. list_dish_tags (M2M) - 会自动删除关联
7. list_dish_pending_tags (M2M) - 会自动删除关联
"""

import os
import sys
import django
from pathlib import Path
from django.db import transaction

# 设置 Django 环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Dish, Rating, Review, UserDishHistory, DishCheckInRecord
from post.models import Post

def analyze_dishes_without_image():
    """分析没有图片的菜品及其相关数据"""
    dishes_without_image = Dish.objects.filter(image__isnull=True) | Dish.objects.filter(image='')
    total_count = dishes_without_image.count()
    
    print("\n" + "="*70)
    print("📊 数据分析 - 没有图片的菜品")
    print("="*70 + "\n")
    
    if total_count == 0:
        print("✅ 数据库中所有菜品都有图片！无需删除操作。\n")
        return None, {}
    
    print(f"🔍 找到 {total_count} 个没有图片的菜品\n")
    
    # 统计相关数据
    stats = {
        'dishes': total_count,
        'ratings': 0,
        'reviews': 0,
        'user_histories': 0,
        'check_in_records': 0,
        'posts': 0,
    }
    
    # 统计关联的评分
    ratings_count = Rating.objects.filter(dish__in=dishes_without_image).count()
    stats['ratings'] = ratings_count
    
    # 统计关联的评论
    reviews_count = Review.objects.filter(dish__in=dishes_without_image).count()
    stats['reviews'] = reviews_count
    
    # 统计关联的用户历史
    histories_count = UserDishHistory.objects.filter(dish__in=dishes_without_image).count()
    stats['user_histories'] = histories_count
    
    # 统计关联的打卡记录
    check_ins_count = DishCheckInRecord.objects.filter(dish__in=dishes_without_image).count()
    stats['check_in_records'] = check_ins_count
    
    # 统计关联的帖子（会被设置为NULL，不会删除）
    posts_count = Post.objects.filter(dish__in=dishes_without_image).count()
    stats['posts'] = posts_count
    
    print("📈 关联数据统计:")
    print(f"   • 菜品数量: {stats['dishes']}")
    print(f"   • 评分记录 (将被删除): {stats['ratings']}")
    print(f"   • 评论记录 (将被删除): {stats['reviews']}")
    print(f"   • 用户历史记录 (将被删除): {stats['user_histories']}")
    print(f"   • 打卡记录 (将被删除): {stats['check_in_records']}")
    print(f"   • 关联帖子 (菜品引用将设为空): {stats['posts']}")
    print()
    
    # 显示部分菜品示例
    sample_dishes = list(dishes_without_image[:10])
    if sample_dishes:
        print("📝 菜品示例 (前10个):")
        for i, dish in enumerate(sample_dishes, 1):
            print(f"   {i}. {dish.name} - {dish.canteen.name} (¥{dish.price})")
        if total_count > 10:
            print(f"   ... 还有 {total_count - 10} 个菜品")
        print()
    
    return dishes_without_image, stats

def delete_dishes_without_image():
    """删除没有图片的菜品及其所有关联数据"""
    
    print("\n" + "="*70)
    print("🗑️  删除没有图片的菜品脚本")
    print("="*70 + "\n")
    
    # 首先分析数据
    dishes_without_image, stats = analyze_dishes_without_image()
    
    if dishes_without_image is None:
        return
    
    # 确认操作
    print("⚠️  警告: 此操作将永久删除以上菜品及其关联数据！")
    print("⚠️  注意: 此操作不可恢复！\n")
    confirm = input("确认继续删除？(yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n❌ 操作已取消")
        return
    
    print("\n🔄 开始删除操作...\n")
    
    try:
        with transaction.atomic():
            # Django ORM 会自动处理 CASCADE 外键，删除关联数据
            # SET_NULL 外键会自动设置为 NULL
            deleted_count = 0
            total = dishes_without_image.count()
            
            for i, dish in enumerate(dishes_without_image, 1):
                dish_name = dish.name
                canteen_name = dish.canteen.name
                
                # 删除菜品（会自动级联删除所有相关数据）
                dish.delete()
                deleted_count += 1
                
                # 显示进度
                if i % 10 == 0 or i == total:
                    progress = (i / total) * 100
                    print(f"⏳ 进度: {i}/{total} ({progress:.1f}%) - "
                          f"最新: {dish_name[:20]}... ({canteen_name})")
            
            print("\n" + "="*70)
            print("✅ 删除完成！")
            print("="*70)
            print(f"\n📊 删除统计:")
            print(f"   • 删除菜品: {deleted_count}")
            print(f"   • 删除评分记录: {stats['ratings']}")
            print(f"   • 删除评论记录: {stats['reviews']}")
            print(f"   • 删除用户历史记录: {stats['user_histories']}")
            print(f"   • 删除打卡记录: {stats['check_in_records']}")
            print(f"   • 更新帖子引用为空: {stats['posts']}")
            print("\n✅ 所有外键约束已正确处理")
            print("="*70 + "\n")
            
    except Exception as e:
        print(f"\n❌ 删除失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  事务已回滚，数据未被修改")

def preview_only():
    """仅预览，不删除"""
    print("\n" + "="*70)
    print("👀 预览模式 - 没有图片的菜品分析")
    print("="*70 + "\n")
    
    analyze_dishes_without_image()
    
    print("💡 提示: 这是预览模式，没有执行任何删除操作")
    print("="*70 + "\n")

if __name__ == '__main__':
    import sys
    
    try:
        # 检查命令行参数
        if len(sys.argv) > 1 and sys.argv[1] == '--preview':
            preview_only()
        else:
            delete_dishes_without_image()
    except KeyboardInterrupt:
        print("\n\n❌ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
