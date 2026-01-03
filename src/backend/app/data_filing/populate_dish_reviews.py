"""
为每个菜品添加真实的评价和评分
使用 DeepSeek API 生成贴近真实场景的评价内容
"""
import os
import sys
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta
import requests
import json
import time

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Dish, Rating, Review
from django.contrib.auth.models import User as AuthUser  # Django 内置 User (用于 Rating/Review)
from login.models import User as LoginUser  # 自定义 User (用于选择用户)


# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-1b99a2e2a88441239e2988bdda668e63"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def call_deepseek_api(dish_name, score, dish_description=""):
    """
    调用 DeepSeek API 生成评价内容
    
    Args:
        dish_name: 菜品名称
        score: 评分 (3.0-5.0)
        dish_description: 菜品描述
        
    Returns:
        生成的评价文本
    """
    # 根据评分确定评价倾向
    if score >= 4.5:
        sentiment = "非常满意，强烈推荐"
        tone = "热情赞美"
    elif score >= 4.0:
        sentiment = "满意，推荐"
        tone = "正面积极"
    elif score >= 3.5:
        sentiment = "一般，有优点也有缺点"
        tone = "中立客观"
    else:
        sentiment = "不太满意，有待改进"
        tone = "轻微批评但建设性"
    
    prompt = f"""请为食堂菜品"{dish_name}"生成一条真实的用户评价。

评分：{score}/5.0
情感倾向：{sentiment}
语气：{tone}
{f'菜品描述：{dish_description}' if dish_description else ''}

要求：
1. 评价要像真实的大学生写的，语气自然、口语化
2. 长度在20-80字之间
3. 可以提到味道、分量、价格、卫生、服务等方面
4. 根据评分体现相应的满意度
5. 避免过于书面化的表达
6. 可以适当使用口语词汇，如"不错"、"还行"、"一般般"等
7. 高分评价要具体说明好在哪里，低分评价要指出可改进之处
8. 不要包含评分数字，只需要评价文字

请直接输出评价内容，不要加任何前缀或说明："""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.9,  # 增加随机性
        "max_tokens": 200
    }
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            # 移除可能的引号
            content = content.strip('"').strip("'").strip()
            return content
        else:
            print(f"API调用失败: {response.status_code} - {response.text}")
            return generate_fallback_review(dish_name, score)
            
    except Exception as e:
        print(f"API调用异常: {str(e)}")
        return generate_fallback_review(dish_name, score)


def generate_fallback_review(dish_name, score):
    """
    当 API 调用失败时的备用评价生成
    """
    good_reviews = [
        f"{dish_name}真的很好吃！分量足，性价比高，推荐！",
        f"超喜欢这个{dish_name}，味道正宗，每次都要吃。",
        f"{dish_name}做得很不错，食材新鲜，下次还会来。",
        f"这家的{dish_name}是我吃过最好的，强烈推荐！",
        f"{dish_name}味道很赞，价格也合理，值得一试。",
    ]
    
    medium_reviews = [
        f"{dish_name}味道还可以，就是分量有点少。",
        f"整体还行，{dish_name}中规中矩，没什么特别的。",
        f"{dish_name}一般般吧，不难吃但也没有很惊艳。",
        f"价格可以接受，{dish_name}味道普通，凑合吃。",
        f"{dish_name}还行，不过有时候味道不太稳定。",
    ]
    
    bad_reviews = [
        f"{dish_name}有点咸了，不太符合我的口味。",
        f"这次的{dish_name}不如以前好吃，希望能改进。",
        f"{dish_name}分量太少了，价格有点贵。",
        f"感觉{dish_name}不太新鲜，有待提高。",
        f"{dish_name}味道一般，性价比不高，不会再买了。",
    ]
    
    if score >= 4.5:
        return random.choice(good_reviews)
    elif score >= 3.5:
        return random.choice(medium_reviews)
    else:
        return random.choice(bad_reviews)


def generate_random_score():
    """
    生成随机评分：3.0, 3.5, 4.0, 4.5, 5.0
    """
    scores = [3.0, 3.5, 4.0, 4.5, 5.0]
    # 使用加权随机，让中高分更常见（符合实际情况）
    weights = [5, 10, 25, 35, 25]  # 倾向于4.0-4.5分
    return Decimal(str(random.choices(scores, weights=weights)[0]))


def generate_random_datetime(days_back=90):
    """
    生成随机的过去时间
    """
    now = datetime.now()
    random_days = random.randint(0, days_back)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    return now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)


def populate_reviews_for_dish(dish, login_users, min_reviews=5, max_reviews=20, use_api=True):
    """
    为单个菜品生成评价
    
    Args:
        dish: 菜品对象
        login_users: login_user 表的用户列表
        min_reviews: 最小评价数
        max_reviews: 最大评价数
        use_api: 是否使用 API（False 则使用备用方案）
    """
    review_count = random.randint(min_reviews, max_reviews)
    print(f"\n正在为 [{dish.name}] 生成 {review_count} 条评价...")
    
    # 随机选择不重复的用户
    if len(login_users) < review_count:
        print(f"警告：用户数量({len(login_users)})少于评价数量({review_count})，部分用户会重复评价")
        selected_login_users = random.choices(login_users, k=review_count)
    else:
        selected_login_users = random.sample(login_users, review_count)
    
    created_count = 0
    skipped_count = 0
    
    for i, login_user in enumerate(selected_login_users, 1):
        try:
            # 通过 username 查找或创建对应的 auth_user
            auth_user, created = AuthUser.objects.get_or_create(
                username=login_user.username,
                defaults={'password': 'unused'}  # 密码不重要，不用于登录
            )
            if created:
                print(f"  [{i}/{review_count}] 创建 auth_user: {login_user.username}")
            
            # 检查是否已存在该用户对该菜品的评分
            if Rating.objects.filter(user=auth_user, dish=dish).exists():
                print(f"  [{i}/{review_count}] 跳过：用户 {login_user.username} 已评价过此菜品")
                skipped_count += 1
                continue
            
            # 生成随机评分
            score = generate_random_score()
            
            # 生成评价内容
            if use_api:
                print(f"  [{i}/{review_count}] 调用 API 生成评价 (评分: {score})...")
                content = call_deepseek_api(
                    dish_name=dish.name,
                    score=float(score),
                    dish_description=dish.description
                )
                # API 限流，避免请求过快
                time.sleep(0.5)
            else:
                content = generate_fallback_review(dish.name, float(score))
            
            print(f"      生成内容: {content[:50]}...")
            
            # 创建评分记录（使用 auth_user）
            rating = Rating.objects.create(
                user=auth_user,
                dish=dish,
                score=score
            )
            
            # 设置随机的创建时间
            random_time = generate_random_datetime()
            rating.created_at = random_time
            rating.updated_at = random_time
            rating.save(update_fields=['created_at', 'updated_at'])
            
            # 创建评论记录（使用 auth_user）
            review = Review.objects.create(
                user=auth_user,
                dish=dish,
                content=content,
                rating=rating,
                published_score=score,
                status='approved'  # 直接设置为已通过
            )
            
            # 设置相同的创建时间
            review.created_at = random_time
            review.updated_at = random_time
            review.save(update_fields=['created_at', 'updated_at'])
            
            created_count += 1
            print(f"      ✓ 成功创建评价")
            
        except Exception as e:
            print(f"  [{i}/{review_count}] 错误：{str(e)}")
            skipped_count += 1
    
    print(f"完成 [{dish.name}]: 成功创建 {created_count} 条，跳过 {skipped_count} 条")
    return created_count, skipped_count


def main():
    """
    主函数
    """
    print("=" * 80)
    print("菜品评价填充脚本")
    print("=" * 80)
    
    # 检查 API Key
    use_api = True
    if DEEPSEEK_API_KEY == 'your-api-key-here':
        print("\n警告：未配置 DEEPSEEK_API_KEY 环境变量")
        print("将使用备用评价生成方案（模板化评价）")
        print("如需使用 AI 生成评价，请设置环境变量：")
        print("  export DEEPSEEK_API_KEY='your-actual-api-key'")
        use_api = False
    else:
        print(f"\n✓ 已配置 DeepSeek API Key: {DEEPSEEK_API_KEY[:10]}...")
    
    # 获取所有菜品
    dishes = list(Dish.objects.all())
    print(f"\n数据库中共有 {len(dishes)} 个菜品")
    
    if not dishes:
        print("错误：数据库中没有菜品数据，请先运行菜品填充脚本")
        return
    
    # 获取所有 login_user 用户
    login_users = list(LoginUser.objects.all())
    print(f"数据库中共有 {len(login_users)} 个用户 (login_user 表)")
    
    if not login_users:
        print("错误：login_user 表中没有用户数据，请先创建用户")
        return
    
    if len(login_users) < 5:
        print(f"警告：用户数量较少({len(login_users)})，建议至少有 20 个用户")
    
    # 询问用户是否继续
    print("\n配置：")
    print(f"  - 每个菜品评价数量: 5-20 条（随机）")
    print(f"  - 评分范围: 3.0-5.0（步长 0.5）")
    print(f"  - 评分分布: 倾向于 4.0-4.5 分")
    print(f"  - 生成方式: {'DeepSeek AI' if use_api else '模板化'}")
    
    confirm = input("\n是否开始生成？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 开始生成
    print("\n" + "=" * 80)
    print("开始生成评价...")
    print("=" * 80)
    
    total_created = 0
    total_skipped = 0
    start_time = time.time()
    
    for idx, dish in enumerate(dishes, 1):
        print(f"\n进度: [{idx}/{len(dishes)}]")
        created, skipped = populate_reviews_for_dish(
            dish=dish,
            login_users=login_users,
            min_reviews=5,
            max_reviews=20,
            use_api=use_api
        )
        total_created += created
        total_skipped += skipped
        
        # 每处理 10 个菜品休息一下
        if idx % 10 == 0:
            print(f"\n已处理 {idx}/{len(dishes)} 个菜品，休息 2 秒...")
            time.sleep(2)
    
    # 统计结果
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("填充完成！")
    print("=" * 80)
    print(f"总计：")
    print(f"  - 处理菜品数: {len(dishes)}")
    print(f"  - 成功创建评价: {total_created}")
    print(f"  - 跳过: {total_skipped}")
    print(f"  - 耗时: {elapsed_time:.2f} 秒")
    print(f"  - 平均每个菜品: {elapsed_time/len(dishes):.2f} 秒")
    
    # 显示数据库统计
    print("\n数据库统计：")
    print(f"  - 总评分数: {Rating.objects.count()}")
    print(f"  - 总评论数: {Review.objects.count()}")
    print(f"  - 已审核通过: {Review.objects.filter(status='approved').count()}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，正在退出...")
    except Exception as e:
        print(f"\n\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
