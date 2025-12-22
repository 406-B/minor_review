"""
自动化填充美食论坛数据脚本
- 创建200个用户（含头像）
- 创建50个帖子（含图片和菜品关联）
- 每个帖子20-100个评论（支持楼中楼回复）
- 使用DeepSeek API生成内容
- 使用百度图片搜索下载图片
"""

import os
import sys
import django
import random
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from django.db import transaction
from django.core.files.base import ContentFile
from openai import OpenAI

# 设置 Django 环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from login.models import User
from list.models import Dish
from post.models import Post, Comment

# DeepSeek API 客户端
client = OpenAI(
    api_key="sk-1b99a2e2a88441239e2988bdda668e63",
    base_url="https://api.deepseek.com"
)

# 配置
TOTAL_USERS = 200
TOTAL_POSTS = 50
DEFAULT_PASSWORD = "75312552159Aa_"
COMMENTS_MIN = 20
COMMENTS_MAX = 100

# 创建下载目录
AVATAR_DIR = Path(BASE_DIR) / "media" / "avatars"
POST_IMAGE_DIR = Path(BASE_DIR) / "media" / "post_images"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
POST_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# Session for image download
session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://image.baidu.com/",
})


def download_image_from_baidu(keyword, save_path, count=1):
    """从百度图片搜索下载图片"""
    try:
        # 先访问一次百度获得真实 Cookie
        session.get("https://image.baidu.com")
        
        url = "https://image.baidu.com/search/acjson"
        params = {
            "tn": "resultjson_com",
            "ipn": "rj",
            "ct": "201326592",
            "cl": "2",
            "lm": "-1",
            "word": keyword,
            "queryWord": keyword,
            "pn": "0",
            "rn": str(count * 3),  # 多获取一些，以防部分失败
        }
        
        resp = session.get(url, params=params, timeout=10)
        data = resp.json()
        
        downloaded = []
        if "data" in data:
            for item in data.get("data", []):
                if len(downloaded) >= count:
                    break
                    
                if isinstance(item, dict) and "thumbURL" in item:
                    img_url = item["thumbURL"]
                    try:
                        img = session.get(img_url, timeout=5).content
                        filename = f"{keyword}_{random.randint(1000, 9999)}_{len(downloaded)}.jpg"
                        file_path = save_path / filename
                        
                        with open(file_path, "wb") as f:
                            f.write(img)
                        
                        downloaded.append(file_path)
                    except Exception as e:
                        print(f"      ⚠️ 图片下载失败: {e}")
                        continue
        
        return downloaded
    except Exception as e:
        print(f"      ❌ 百度图片搜索失败: {e}")
        return []


def call_deepseek_api(prompt, temperature=0.8):
    """调用DeepSeek API生成内容"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt},
            ],
            stream=False,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"      ❌ API调用失败: {e}")
        return None


def generate_username():
    """生成随机用户名"""
    prefixes = ["美食家", "吃货", "foodie", "味道", "品味", "食客", "饕餮", "美味", "口福", "食神"]
    suffixes = ["小王", "小李", "小张", "阿明", "阿强", "阿华", "佳佳", "欣欣", "乐乐", "萌萌"]
    numbers = random.randint(100, 9999)
    
    if random.random() > 0.5:
        return f"{random.choice(prefixes)}{random.choice(suffixes)}{numbers}"
    else:
        return f"{random.choice(prefixes)}{numbers}"


def create_users():
    """创建200个用户"""
    print("\n" + "="*70)
    print("👥 创建用户")
    print("="*70 + "\n")
    
    users = []
    
    # 下载头像关键词列表
    avatar_keywords = ["头像", "卡通头像", "可爱头像", "动漫头像"]
    
    for i in range(TOTAL_USERS):
        username = generate_username()
        
        # 确保用户名唯一
        while User.objects.filter(username=username).exists():
            username = generate_username()
        
        # 生成昵称
        prompt = f"请生成一个中文昵称，适合美食论坛使用，2-6个字，只返回昵称本身，不要其他内容。"
        nickname = call_deepseek_api(prompt, temperature=1.0)
        if not nickname or len(nickname) > 10:
            nickname = username
        
        # 下载头像
        avatar_path = None
        if i % 10 == 0 or i == 0:  # 每10个用户下载一批头像
            keyword = random.choice(avatar_keywords)
            downloaded = download_image_from_baidu(keyword, AVATAR_DIR, count=10)
            if downloaded:
                avatar_path = random.choice(downloaded)
        
        # 创建用户
        user = User(
            username=username,
            password=DEFAULT_PASSWORD,  # 实际应该使用哈希密码
            nickname=nickname
        )
        
        # 设置头像
        if avatar_path and avatar_path.exists():
            with open(avatar_path, 'rb') as f:
                user.avatar.save(avatar_path.name, ContentFile(f.read()), save=False)
        
        user.save()
        users.append(user)
        
        if (i + 1) % 20 == 0:
            print(f"   ✅ 已创建 {i + 1}/{TOTAL_USERS} 个用户")
    
    print(f"\n✅ 成功创建 {len(users)} 个用户\n")
    return users


def create_posts_and_comments(users):
    """创建50个帖子和评论"""
    print("\n" + "="*70)
    print("📝 创建帖子和评论")
    print("="*70 + "\n")
    
    # 获取所有菜品
    dishes = list(Dish.objects.all())
    if not dishes:
        print("❌ 数据库中没有菜品数据！")
        return
    
    print(f"📊 找到 {len(dishes)} 个菜品")
    print(f"👥 有 {len(users)} 个用户可用\n")
    
    for post_idx in range(TOTAL_POSTS):
        print(f"📝 创建帖子 {post_idx + 1}/{TOTAL_POSTS}")
        
        # 随机选择作者
        author = random.choice(users)
        
        # 随机决定是否关联菜品（80%概率关联）
        dish = None
        if random.random() < 0.8:
            dish = random.choice(dishes)
        
        # 生成帖子标题和内容
        if dish:
            prompt = f"""请为美食论坛生成一篇帖子。
菜品名称：{dish.name}
菜品价格：¥{dish.price}
食堂：{dish.canteen.name}

请生成：
1. 标题（15-30字，吸引人）
2. 内容（150-300字，分享美食体验）

格式：
标题：[标题内容]
内容：[内容]

要求：内容要真实、生动、有细节描述。"""
        else:
            prompt = f"""请为美食论坛生成一篇帖子。
主题：校园美食、食堂体验、美食推荐等

请生成：
1. 标题（15-30字，吸引人）
2. 内容（150-300字，分享美食体验）

格式：
标题：[标题内容]
内容：[内容]

要求：内容要真实、生动、有细节描述。"""
        
        response = call_deepseek_api(prompt, temperature=0.9)
        if not response:
            print("   ⚠️ API调用失败，跳过")
            continue
        
        # 解析标题和内容
        lines = response.split('\n')
        subject = ""
        content = ""
        
        for line in lines:
            if line.startswith("标题：") or line.startswith("标题:"):
                subject = line.replace("标题：", "").replace("标题:", "").strip()
            elif line.startswith("内容：") or line.startswith("内容:"):
                content = line.replace("内容：", "").replace("内容:", "").strip()
            elif content:
                content += "\n" + line
        
        if not subject or not content:
            subject = "美食分享"
            content = response
        
        # 随机决定是否添加图片（60%概率）
        images = []
        if random.random() < 0.6:
            image_count = random.randint(1, 4)
            keyword = dish.name if dish else "美食"
            downloaded = download_image_from_baidu(keyword, POST_IMAGE_DIR, count=image_count)
            
            if downloaded:
                # 保存为相对路径
                for img_path in downloaded:
                    rel_path = f"post_images/{img_path.name}"
                    images.append(rel_path)
        
        # 创建帖子
        post = Post.objects.create(
            author=author,
            subject=subject[:200],
            content=content,
            images=images,
            dish=dish,
            status='approved',  # 直接通过审核
            likes_count=random.randint(0, 200)
        )
        
        # 随机调整创建时间（过去30天内）
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        post.created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        post.save()
        
        print(f"   ✅ 帖子: {subject[:30]}...")
        print(f"      作者: {author.nickname}")
        if dish:
            print(f"      关联菜品: {dish.name}")
        if images:
            print(f"      图片数量: {len(images)}")
        
        # 创建评论
        comments_count = random.randint(COMMENTS_MIN, COMMENTS_MAX)
        create_comments_for_post(post, users, comments_count, dish)
        
        print()
        
        # 避免API频率限制
        time.sleep(1)
    
    print(f"✅ 成功创建 {TOTAL_POSTS} 个帖子\n")


def create_comments_for_post(post, users, count, dish):
    """为帖子创建评论（包含楼中楼）"""
    print(f"   💬 创建 {count} 个评论...")
    
    created_comments = []
    
    # 创建一级评论（占60%）
    first_level_count = int(count * 0.6)
    
    for i in range(first_level_count):
        author = random.choice(users)
        
        # 生成评论内容
        if dish:
            prompt = f"""请为美食论坛帖子生成一条评论。
帖子主题：{post.subject}
关联菜品：{dish.name}

要求：
- 10-80字
- 自然真实，像普通用户评论
- 可以是赞同、补充、提问、分享经验等
- 只返回评论内容本身

评论："""
        else:
            prompt = f"""请为美食论坛帖子生成一条评论。
帖子主题：{post.subject}

要求：
- 10-80字
- 自然真实，像普通用户评论
- 可以是赞同、补充、提问、分享经验等
- 只返回评论内容本身

评论："""
        
        content = call_deepseek_api(prompt, temperature=1.0)
        if not content:
            content = random.choice([
                "说得太对了！",
                "我也觉得很好吃",
                "下次一定要去试试",
                "感谢分享！",
                "看起来不错",
            ])
        
        comment = Comment.objects.create(
            post=post,
            author=author,
            content=content[:500],
            status='approved',
            likes_count=random.randint(0, 50)
        )
        
        # 随机调整创建时间（在帖子创建之后）
        hours_after = random.randint(1, 72)
        comment.created_at = post.created_at + timedelta(hours=hours_after)
        comment.save()
        
        created_comments.append(comment)
        
        # 避免API频率限制
        if i % 5 == 0:
            time.sleep(0.5)
    
    # 创建二级及以上评论（楼中楼，占40%）
    reply_count = count - first_level_count
    
    for i in range(reply_count):
        if not created_comments:
            break
        
        # 随机选择一个评论作为父评论
        parent = random.choice(created_comments)
        author = random.choice(users)
        
        # 生成回复内容
        prompt = f"""请为美食论坛评论生成一条回复。
原评论：{parent.content}

要求：
- 10-60字
- 针对原评论进行回复
- 自然真实
- 只返回回复内容本身

回复："""
        
        content = call_deepseek_api(prompt, temperature=1.0)
        if not content:
            content = random.choice([
                "哈哈，确实是这样",
                "我也这么觉得",
                "说得好！",
                "有道理",
                "同感",
            ])
        
        reply = Comment.objects.create(
            post=post,
            author=author,
            content=content[:500],
            parent=parent,
            status='approved',
            likes_count=random.randint(0, 30)
        )
        
        # 回复时间在父评论之后
        hours_after = random.randint(1, 48)
        reply.created_at = parent.created_at + timedelta(hours=hours_after)
        reply.save()
        
        # 将回复也加入列表，支持更深层次的楼中楼（小概率）
        if random.random() < 0.3:
            created_comments.append(reply)
        
        # 避免API频率限制
        if i % 5 == 0:
            time.sleep(0.5)
    
    # 更新帖子的评论数
    post.comments_count = count
    post.save(update_fields=['comments_count'])


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 美食论坛自动化填充脚本")
    print("="*70)
    print(f"\n配置:")
    print(f"  • 用户数量: {TOTAL_USERS}")
    print(f"  • 帖子数量: {TOTAL_POSTS}")
    print(f"  • 统一密码: {DEFAULT_PASSWORD}")
    print(f"  • 每帖评论: {COMMENTS_MIN}-{COMMENTS_MAX}")
    print()
    
    confirm = input("⚠️  此操作将向数据库添加大量数据，确认继续？(yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("\n❌ 操作已取消")
        return
    
    start_time = time.time()
    
    try:
        # 创建用户
        users = create_users()
        
        # 创建帖子和评论
        create_posts_and_comments(users)
        
        elapsed = time.time() - start_time
        
        print("="*70)
        print("✅ 填充完成！")
        print("="*70)
        print(f"\n📊 统计:")
        print(f"  • 用户数: {User.objects.count()}")
        print(f"  • 帖子数: {Post.objects.count()}")
        print(f"  • 评论数: {Comment.objects.count()}")
        print(f"  • 耗时: {elapsed/60:.1f} 分钟")
        print(f"\n💾 图片保存路径:")
        print(f"  • 头像: media/avatars/")
        print(f"  • 帖子图片: media/post_images/")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
