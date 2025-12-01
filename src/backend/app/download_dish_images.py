"""
下载菜品图片脚本
从占位图服务下载图片并保存到本地
"""
import os
import sys
import django
import requests
from pathlib import Path

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Dish
from django.core.files.base import ContentFile


def download_and_save_image(dish):
    """为菜品下载并保存图片"""
    # 生成图片URL
    seed = abs(hash(dish.name)) % 1000
    image_url = f"https://picsum.photos/seed/{seed}/800/600"
    
    try:
        # 下载图片
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # 生成文件名
        filename = f"dish_{dish.id}_{seed}.jpg"
        
        # 保存到ImageField
        dish.image.save(filename, ContentFile(response.content), save=True)
        
        return True
    except Exception as e:
        print(f"  失败: {dish.name} - {str(e)}")
        return False


def main():
    print("="*70)
    print("开始下载菜品图片")
    print("="*70)
    print()
    
    # 获取所有没有图片的菜品
    dishes_without_image = Dish.objects.filter(image='')
    
    total = dishes_without_image.count()
    
    if total == 0:
        print("所有菜品都已有图片！")
        return
    
    print(f"找到 {total} 道菜品需要下载图片")
    print("注意：这可能需要一些时间...")
    print()
    
    success_count = 0
    fail_count = 0
    
    for i, dish in enumerate(dishes_without_image, 1):
        print(f"[{i}/{total}] 下载 {dish.name} 的图片...", end=' ')
        
        if download_and_save_image(dish):
            print("✓")
            success_count += 1
        else:
            fail_count += 1
        
        # 每10个打印一次进度
        if i % 10 == 0:
            print(f"  进度: {i}/{total} ({i/total*100:.1f}%)")
    
    print()
    print("="*70)
    print(f"完成！成功: {success_count}, 失败: {fail_count}")
    print("="*70)


if __name__ == '__main__':
    main()
