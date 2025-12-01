"""
自动生成菜品数据脚本
为每个餐厅生成大量真实的菜品数据
"""
import os
import sys
import django
import random
from decimal import Decimal

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Canteen, Dish, Tag, Floor, Window


# 中式菜品名称库
CHINESE_DISHES = {
    '主食': [
        '红烧肉盖饭', '宫保鸡丁盖饭', '麻婆豆腐盖饭', '鱼香肉丝盖饭', '青椒肉丝盖饭',
        '番茄炒蛋盖饭', '木须肉盖饭', '回锅肉盖饭', '糖醋里脊盖饭', '干煸豆角盖饭',
        '炸酱面', '担担面', '热干面', '牛肉拉面', '刀削面', '臊子面', '油泼面',
        '阳春面', '炒面', '炒米粉', '炒河粉', '炒年糕',
        '扬州炒饭', '蛋炒饭', '虾仁炒饭', '菠萝炒饭', '什锦炒饭',
        '鸡蛋灌饼', '手抓饼', '煎饼果子', '肉夹馍', '羊肉泡馍',
        '水饺', '煎饺', '蒸饺', '小笼包', '灌汤包', '韭菜盒子', '锅贴'
    ],
    '川菜': [
        '麻辣香锅', '水煮鱼', '水煮肉片', '酸菜鱼', '剁椒鱼头',
        '辣子鸡', '口水鸡', '夫妻肺片', '毛血旺', '麻婆豆腐',
        '宫保鸡丁', '鱼香肉丝', '回锅肉', '东坡肉', '粉蒸肉',
        '干锅土豆片', '干锅花菜', '干锅包菜', '干锅千叶豆腐'
    ],
    '粤菜': [
        '白切鸡', '烧鹅', '烧鸭', '叉烧', '蜜汁叉烧',
        '清蒸鲈鱼', '豉汁蒸排骨', '虾饺', '烧卖', '肠粉',
        '煲仔饭', '艇仔粥', '及第粥', '皮蛋瘦肉粥',
        '广式点心拼盘', '流沙包', '蛋挞', '萝卜糕', '马蹄糕'
    ],
    '素菜': [
        '地三鲜', '干煸四季豆', '手撕包菜', '清炒油麦菜', '蒜蓉油麦菜',
        '炒青菜', '蒜蓉西兰花', '清炒豆芽', '酸辣土豆丝', '醋溜白菜',
        '红烧茄子', '炒豆角', '干锅千叶豆腐', '家常豆腐', '香干炒肉',
        '木耳炒鸡蛋', '西红柿炒鸡蛋', '韭菜炒鸡蛋', '青椒炒蛋'
    ],
    '汤羹': [
        '紫菜蛋花汤', '西红柿蛋汤', '酸辣汤', '玉米排骨汤', '冬瓜排骨汤',
        '萝卜牛腩汤', '莲藕排骨汤', '银耳莲子羹', '红豆薏米粥', '绿豆汤',
        '三鲜汤', '疙瘩汤', '馄饨汤', '鱼丸汤', '肉丸汤'
    ],
    '小吃': [
        '煎饼', '油条', '麻团', '糖三角', '豆包', '花卷', '馒头',
        '烧饼', '糖糕', '炸糕', '驴打滚', '艾窝窝',
        '春卷', '炸春卷', '蛋黄酥', '老婆饼', '绿豆糕', '桃酥',
        '麻花', '薯片', '薯条', '炸鸡块', '鸡米花', '鸡翅', '鸡腿'
    ],
    '烧烤': [
        '羊肉串', '牛肉串', '鸡肉串', '里脊肉串', '培根卷',
        '烤鸡翅', '烤鸡腿', '烤玉米', '烤茄子', '烤韭菜',
        '烤土豆', '烤香菇', '烤鱿鱼', '烤鱼豆腐', '烤面筋',
        '烤馒头片', '烤年糕', '烤冷面'
    ],
    '西餐': [
        '意大利面', '披萨', '汉堡', '三明治', '热狗',
        '炸鸡排', '鸡排饭', '牛排饭', '黑椒牛柳',
        '沙拉', '凯撒沙拉', '水果沙拉', '蔬菜沙拉',
        '奶油蘑菇汤', '罗宋汤', '玉米浓汤'
    ],
    '饮品': [
        '豆浆', '紫米粥', '八宝粥', '小米粥', '玉米粥',
        '珍珠奶茶', '柠檬茶', '红茶', '绿茶', '乌龙茶',
        '可乐', '雪碧', '橙汁', '苹果汁', '西瓜汁', '酸梅汤',
        '豆奶', '酸奶', '牛奶', '咖啡', '拿铁', '美式咖啡'
    ]
}

# 菜品描述模板
DESCRIPTIONS = [
    '精选优质食材，现炒现做，色香味俱全。{special}火候掌握恰到好处，{texture}口感丰富，营养均衡。适合日常用餐，深受师生喜爱。',
    '传统工艺制作，{special}选用新鲜{ingredients}，经过{cooking_method}烹饪而成。{texture}味道鲜美，回味无穷。每日限量供应，售完即止。',
    '招牌菜品，{special}采用秘制配方，{cooking_method}精心烹制。色泽{color}，香气扑鼻，{texture}入口难忘。性价比超高，是食堂的人气之选。',
    '健康营养，{special}低脂少油，保留食材原汁原味。{texture}清淡可口，适合注重健康饮食的同学。富含{nutrients}，有助于补充日常所需营养。',
    '地道{cuisine}风味，{special}传承正宗做法，{cooking_method}烹饪。{texture}味道浓郁，{spicy_level}层次分明。让你在校园就能品尝到家乡味道。',
    '创新菜品，{special}融合现代烹饪技艺，{texture}口感独特。选用当季{ingredients}，新鲜健康。是食堂推出的特色菜系，值得一试。',
    '经典美食，{special}流传多年的传统做法，{cooking_method}烹制。{color}诱人，{texture}口感极佳。分量十足，绝对物超所值。',
    '精品套餐，{special}营养搭配合理，荤素均衡。{texture}满足一餐所需，{portion}适中。是学习工作后快速补充能量的理想选择。'
]

# 特色描述
SPECIALS = [
    '采用传统工艺，', '精选当季食材，', '大厨推荐，', '独家秘制，',
    '现点现做，', '新鲜出炉，', '特别推荐，', '限时供应，',
    '精心烹制，', '匠心之作，', '食堂特色，', '学生最爱，'
]

# 食材
INGREDIENTS = [
    '蔬菜', '肉类', '海鲜', '豆制品', '菌菇类', '时令蔬菜',
    '有机蔬菜', '当季水果', '优质大米', '新鲜面粉'
]

# 烹饪方法
COOKING_METHODS = [
    '爆炒', '清蒸', '红烧', '煎炸', '炖煮', '烘烤',
    '水煮', '干煸', '清炒', '慢炖', '快炒', '小火慢煨'
]

# 口感描述
TEXTURES = [
    '鲜嫩多汁，', '酥脆可口，', '软糯香甜，', '爽滑细腻，',
    '鲜香诱人，', '香辣过瘾，', '清爽不腻，', '浓香四溢，',
    '外酥里嫩，', '入口即化，', '弹牙爽口，', '醇厚绵长，'
]

# 颜色描述
COLORS = [
    '金黄', '红润', '翠绿', '诱人', '鲜艳', '明亮',
    '光泽', '亮丽', '油润', '鲜红'
]

# 营养成分
NUTRIENTS = [
    '蛋白质', '维生素', '膳食纤维', '矿物质', '优质蛋白',
    '多种维生素', '钙质', '铁元素', '氨基酸'
]

# 菜系
CUISINES = [
    '川菜', '粤菜', '湘菜', '鲁菜', '淮扬菜', '浙菜',
    '闽菜', '徽菜', '东北菜', '西北菜'
]

# 辣度
SPICY_LEVELS = [
    '不辣', '微辣', '中辣', '重辣', '特辣',
    '香辣适中，', '麻辣鲜香，', '清淡爽口，'
]

# 分量
PORTIONS = [
    '分量足', '适中', '超大份', '标准份', '精致小份'
]

# 标签库
TAG_CATEGORIES = {
    '口味': ['麻辣', '酸辣', '香辣', '清淡', '鲜香', '甜味', '咸鲜', '五香', '孜然味', '蒜香'],
    '特色': ['招牌菜', '人气推荐', '新品上市', '限时特惠', '季节限定', '大厨推荐', '学生最爱'],
    '饮食习惯': ['素食', '清真', '无辣', '低脂', '低糖', '高蛋白', '粗粮'],
    '烹饪方式': ['现炒', '清蒸', '红烧', '煎炸', '烧烤', '炖煮', '凉拌'],
    '餐次': ['早餐', '午餐', '晚餐', '夜宵', '下午茶'],
    '食材': ['牛肉', '猪肉', '鸡肉', '羊肉', '海鲜', '豆制品', '蔬菜', '面食', '米饭'],
    '营养': ['高蛋白', '低卡路里', '富含维生素', '补钙', '补铁', '营养均衡']
}


def generate_description(dish_name, category):
    """生成菜品描述"""
    template = random.choice(DESCRIPTIONS)
    
    description = template.format(
        special=random.choice(SPECIALS),
        ingredients=random.choice(INGREDIENTS),
        cooking_method=random.choice(COOKING_METHODS),
        texture=random.choice(TEXTURES),
        color=random.choice(COLORS),
        nutrients=random.choice(NUTRIENTS),
        cuisine=random.choice(CUISINES),
        spicy_level=random.choice(SPICY_LEVELS),
        portion=random.choice(PORTIONS)
    )
    
    return description


def generate_price(category):
    """根据菜品类别生成合理价格"""
    price_ranges = {
        '主食': (8, 18),
        '川菜': (12, 25),
        '粤菜': (15, 30),
        '素菜': (6, 12),
        '汤羹': (3, 8),
        '小吃': (2, 8),
        '烧烤': (3, 15),
        '西餐': (15, 35),
        '饮品': (3, 10)
    }
    
    min_price, max_price = price_ranges.get(category, (5, 20))
    price = random.uniform(min_price, max_price)
    
    # 取整到.0或.5
    price = round(price * 2) / 2
    return Decimal(str(price))


def generate_rating():
    """生成评分 (3.5-5.0)"""
    rating = random.uniform(3.5, 5.0)
    return Decimal(str(round(rating, 2)))


def select_tags(dish_name, category):
    """为菜品选择合适的标签"""
    tags = []
    
    # 根据菜品名称和类别智能选择标签
    if '辣' in dish_name or category == '川菜':
        tags.extend(['麻辣', '香辣'])
    if '素' in dish_name or '蔬菜' in dish_name or category == '素菜':
        tags.append('素食')
    if '牛肉' in dish_name:
        tags.append('牛肉')
    if '鸡' in dish_name:
        tags.append('鸡肉')
    if '猪' in dish_name or '肉' in dish_name:
        tags.append('猪肉')
    if '鱼' in dish_name or '虾' in dish_name:
        tags.append('海鲜')
    if '豆腐' in dish_name:
        tags.append('豆制品')
    if '面' in dish_name or '饭' in dish_name:
        tags.append('主食')
    if '汤' in dish_name or '粥' in dish_name:
        tags.append('汤羹')
    if category == '西餐':
        tags.append('西餐')
    if category == '烧烤':
        tags.append('烧烤')
    
    # 随机添加一些特色标签
    if random.random() > 0.7:
        tags.append(random.choice(['招牌菜', '人气推荐', '大厨推荐']))
    
    # 添加烹饪方式
    if random.random() > 0.6:
        tags.append(random.choice(['现炒', '清蒸', '红烧', '煎炸']))
    
    # 添加营养标签
    if random.random() > 0.7:
        tags.append(random.choice(['营养均衡', '高蛋白', '低卡路里']))
    
    return list(set(tags))  # 去重


def create_tags():
    """创建所有标签"""
    print("创建标签...")
    created_count = 0
    
    for category, tag_list in TAG_CATEGORIES.items():
        for tag_name in tag_list:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                created_count += 1
                print(f"  ✓ 创建标签: {tag_name}")
    
    print(f"\n总计: 创建了 {created_count} 个新标签\n")
    return Tag.objects.all()


def generate_dishes_for_canteen(canteen, dishes_per_category):
    """为单个餐厅生成菜品"""
    print(f"\n{'='*60}")
    print(f"正在为 [{canteen.name}] 生成菜品...")
    print(f"{'='*60}\n")
    
    all_tags = list(Tag.objects.all())
    total_created = 0
    
    for category, dish_names in CHINESE_DISHES.items():
        # 从该类别随机选择指定数量的菜品
        selected_dishes = random.sample(
            dish_names, 
            min(dishes_per_category, len(dish_names))
        )
        
        for dish_name in selected_dishes:
            # 检查是否已存在
            if Dish.objects.filter(name=dish_name, canteen=canteen).exists():
                continue
            
            # 生成菜品数据
            description = generate_description(dish_name, category)
            price = generate_price(category)
            rating = generate_rating()
            
            # 创建菜品
            dish = Dish.objects.create(
                name=dish_name,
                description=description,
                price=price,
                canteen=canteen,
                rating=rating,
                view_count=random.randint(10, 500)
            )
            
            # 添加标签
            tag_names = select_tags(dish_name, category)
            for tag_name in tag_names:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    dish.tags.add(tag)
                except Tag.DoesNotExist:
                    pass
            
            # 随机添加一些 pending tags
            if random.random() > 0.7:
                pending_tag_count = random.randint(1, 3)
                pending_tags = random.sample(all_tags, min(pending_tag_count, len(all_tags)))
                for tag in pending_tags:
                    dish.pending_tags.add(tag)
            
            total_created += 1
            print(f"  ✓ {dish_name} - ¥{price} - {rating}分")
    
    print(f"\n[{canteen.name}] 共创建 {total_created} 道菜品\n")
    return total_created


def main():
    """主函数"""
    print("\n" + "="*60)
    print("食堂菜品数据自动生成器")
    print("="*60 + "\n")
    
    # 创建标签
    create_tags()
    
    # 获取所有餐厅
    canteens = Canteen.objects.all()
    
    if not canteens.exists():
        print("❌ 错误: 数据库中没有餐厅数据！")
        print("请先创建餐厅数据。")
        return
    
    print(f"找到 {canteens.count()} 个餐厅\n")
    
    # 设置每个类别生成的菜品数量
    dishes_per_category = 5  # 每个类别5道菜
    
    total_dishes = 0
    
    # 为每个餐厅生成菜品
    for canteen in canteens:
        count = generate_dishes_for_canteen(canteen, dishes_per_category)
        total_dishes += count
    
    # 统计信息
    print("\n" + "="*60)
    print("生成完成！")
    print("="*60)
    print(f"\n总计:")
    print(f"  - 餐厅数量: {canteens.count()}")
    print(f"  - 菜品总数: {total_dishes}")
    print(f"  - 标签总数: {Tag.objects.count()}")
    print(f"  - 平均每个餐厅: {total_dishes // canteens.count() if canteens.count() > 0 else 0} 道菜")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
