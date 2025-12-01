"""
食堂数据自动生成工具
为餐厅创建楼层、窗口和菜品数据

使用方法:
    python generate_canteen_data.py                    # 快速生成（每餐厅40-60道菜）
    python generate_canteen_data.py -n 100             # 每餐厅生成100道菜
    python generate_canteen_data.py --clear            # 清空现有数据并重新生成
    python generate_canteen_data.py --clear-only       # 仅清空数据，不生成新数据
    python generate_canteen_data.py --stats            # 查看数据统计
    python generate_canteen_data.py --download-images  # 下载菜品图片
    python generate_canteen_data.py --min-price 5 --max-price 30  # 自定义价格范围
"""
import os
import sys
import django
import random
import argparse
from decimal import Decimal

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from list.models import Canteen, Dish, Tag, Floor, Window
from django.db.models import Avg, Count, Max, Min


# 窗口名称模板
WINDOW_NAMES = [
    "1号窗口", "2号窗口", "3号窗口", "4号窗口", "5号窗口",
    "6号窗口", "7号窗口", "8号窗口", "9号窗口", "10号窗口",
    "川菜窗口", "粤菜窗口", "素菜窗口", "面食窗口", "盖浇饭窗口",
    "特色窗口", "快餐窗口", "小吃窗口", "饮品窗口", "西餐窗口",
    "清真窗口", "烧烤窗口", "汤粥窗口", "炒菜窗口", "蒸菜窗口"
]


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
        '煎饼果子', '肉夹馍', '凉皮', '肉丸', '鸡蛋仔',
        '炸鸡', '炸鸡腿', '炸鸡翅', '薯条', '鸡米花',
        '春卷', '锅贴', '生煎包', '油条', '麻团', '糖糕',
        '臭豆腐', '烤冷面', '章鱼小丸子', '铁板鱿鱼'
    ],
    '烧烤': [
        '羊肉串', '牛肉串', '鸡翅', '鸡腿', '鸡心',
        '烤韭菜', '烤茄子', '烤玉米', '烤土豆', '烤香菇',
        '烤鱿鱼', '烤鱼', '烤生蚝', '烤扇贝',
        '烤面筋', '烤豆腐', '烤馒头片'
    ],
    '西餐': [
        '牛排', '猪排', '鸡排', '羊排',
        '意大利面', '意式肉酱面', '培根意面', '海鲜意面',
        '披萨', '玛格丽特披萨', '夏威夷披萨', '培根披萨',
        '汉堡', '牛肉汉堡', '鸡腿堡', '鱼肉堡',
        '沙拉', '凯撒沙拉', '水果沙拉', '蔬菜沙拉'
    ],
    '饮品': [
        '珍珠奶茶', '红茶', '绿茶', '奶茶', '果茶',
        '柠檬水', '西瓜汁', '橙汁', '苹果汁', '葡萄汁',
        '豆浆', '酸奶', '牛奶', '咖啡', '拿铁',
        '可乐', '雪碧', '芬达', '冰红茶', '冰绿茶'
    ]
}


# 标签数据按类别分类
TAG_CATEGORIES = {
    '主食': ['主食', '米饭', '面条', '饺子', '包子', '饼类', '炒饭'],
    '川菜': ['川菜', '麻辣', '香辣', '水煮', '干锅', '下饭'],
    '粤菜': ['粤菜', '清淡', '蒸菜', '烧味', '煲仔', '粥类', '点心'],
    '素菜': ['素菜', '蔬菜', '健康', '清炒', '凉拌'],
    '汤羹': ['汤', '羹', '粥', '滋补', '养生'],
    '小吃': ['小吃', '油炸', '快餐', '零食'],
    '烧烤': ['烧烤', '烤串', '夜宵', '炭火'],
    '西餐': ['西餐', '牛排', '意面', '披萨', '汉堡', '沙拉'],
    '饮品': ['饮品', '奶茶', '果汁', '咖啡', '冷饮'],
    '通用': [
        '热销', '推荐', '新品', '经典', '特色',
        '营养', '美味', '实惠', '份量足',
        '午餐', '晚餐', '快手菜', '下饭',
        '适合分享', '单人份'
    ]
}


def create_floors_and_windows(canteen, min_floors=1, max_floors=3, min_windows=3, max_windows=8):
    """为餐厅创建楼层和窗口"""
    num_floors = random.randint(min_floors, max_floors)
    floors = []
    
    for i in range(1, num_floors + 1):
        floor, created = Floor.objects.get_or_create(
            canteen=canteen,
            name=f"{i}楼",
            defaults={'order': i}
        )
        floors.append(floor)
        
        if created:
            num_windows = random.randint(min_windows, max_windows)
            available_names = WINDOW_NAMES.copy()
            random.shuffle(available_names)
            
            for j in range(num_windows):
                if j < len(available_names):
                    window_name = available_names[j]
                else:
                    window_name = f"{j+1}号窗口"
                
                Window.objects.get_or_create(
                    floor=floor,
                    name=window_name,
                    defaults={'order': j + 1}
                )
    
    return floors


def create_tags():
    """创建所有标签"""
    created_tags = {}
    tag_count = 0
    
    for category, tags in TAG_CATEGORIES.items():
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            created_tags[tag_name] = tag
            if created:
                tag_count += 1
    
    return created_tags, tag_count


def generate_description(dish_name, category):
    """根据菜品名称和类别生成描述"""
    templates = [
        f"{dish_name}是一道经典的{category}菜品，选用优质食材，经过精心烹制而成。口感{random.choice(['鲜美', '香脆', '软糯', '嫩滑', '爽口'])}，{random.choice(['色泽诱人', '香气扑鼻', '营养丰富', '老少皆宜'])}。",
        f"精选{random.choice(['新鲜', '上等', '优质', '当季'])}食材制作的{dish_name}，{random.choice(['传统工艺', '独家秘方', '精心调制', '匠心烹饪'])}，{random.choice(['味道鲜美', '口感绝佳', '回味无穷', '深受好评'])}。",
        f"{dish_name}采用{random.choice(['传统', '现代', '创新', '特色'])}烹饪技法，{random.choice(['保留了食材的原汁原味', '完美融合多种风味', '营养与美味兼具', '是本餐厅的招牌菜品之一'])}。",
        f"这道{dish_name}{random.choice(['色香味俱全', '深受食客喜爱', '是本店特色', '广受好评'])}，{random.choice(['适合各个年龄段', '营养均衡', '健康美味', '物美价廉'])}，值得品尝。"
    ]
    
    description = random.choice(templates)
    
    details = [
        f"每份{random.choice(['分量足', '精致小巧', '适中', '超大份'])}。",
        f"{random.choice(['推荐搭配米饭食用', '可单独享用', '适合多人分享', '是下饭的好选择'])}。",
        f"{random.choice(['本店畅销菜品', '厨师推荐', '顾客最爱', '必点菜品'])}。"
    ]
    
    if random.random() > 0.5:
        description += " " + random.choice(details)
    
    return description


def generate_price(category, min_price=None, max_price=None):
    """根据类别生成合理的价格"""
    default_ranges = {
        '主食': (8, 18),
        '川菜': (12, 28),
        '粤菜': (15, 35),
        '素菜': (6, 15),
        '汤羹': (5, 12),
        '小吃': (5, 15),
        '烧烤': (2, 8),
        '西餐': (20, 45),
        '饮品': (5, 15)
    }
    
    default_min, default_max = default_ranges.get(category, (8, 20))
    
    # 如果指定了全局价格范围，使用全局范围
    if min_price is not None and max_price is not None:
        price = round(random.uniform(min_price, max_price), 1)
    else:
        price = round(random.uniform(default_min, default_max), 1)
    
    return Decimal(str(price))


def generate_rating():
    """生成评分 (3.5-5.0之间)"""
    rating = round(random.uniform(3.5, 5.0), 2)
    return Decimal(str(rating))


def clear_data():
    """清空所有菜品、标签、楼层和窗口数据"""
    print("\n清空现有数据...")
    
    dish_count = Dish.objects.count()
    tag_count = Tag.objects.count()
    floor_count = Floor.objects.count()
    window_count = Window.objects.count()
    
    Dish.objects.all().delete()
    Tag.objects.all().delete()
    Floor.objects.all().delete()
    Window.objects.all().delete()
    
    print(f"  ✓ 删除了 {dish_count} 道菜品")
    print(f"  ✓ 删除了 {tag_count} 个标签")
    print(f"  ✓ 删除了 {floor_count} 个楼层")
    print(f"  ✓ 删除了 {window_count} 个窗口")


def show_statistics():
    """显示数据统计"""
    print("\n" + "="*70)
    print("数据统计报告")
    print("="*70 + "\n")
    
    canteen_count = Canteen.objects.count()
    dish_count = Dish.objects.count()
    tag_count = Tag.objects.count()
    floor_count = Floor.objects.count()
    window_count = Window.objects.count()
    
    print("📊 基础数据:")
    print(f"  ✓ 餐厅数量: {canteen_count}")
    print(f"  ✓ 菜品总数: {dish_count}")
    print(f"  ✓ 标签总数: {tag_count}")
    print(f"  ✓ 楼层总数: {floor_count}")
    print(f"  ✓ 窗口总数: {window_count}")
    
    if canteen_count > 0:
        print(f"  ✓ 平均每餐厅: {dish_count / canteen_count:.1f} 道菜")
        if floor_count > 0:
            print(f"  ✓ 平均每餐厅: {floor_count / canteen_count:.1f} 层楼")
        if window_count > 0:
            print(f"  ✓ 平均每餐厅: {window_count / canteen_count:.1f} 个窗口")
    
    if dish_count > 0:
        price_stats = Dish.objects.aggregate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        rating_stats = Dish.objects.aggregate(
            avg_rating=Avg('rating'),
            min_rating=Min('rating'),
            max_rating=Max('rating')
        )
        
        print("\n💰 价格分析:")
        print(f"  ✓ 平均价格: ¥{price_stats['avg_price']:.2f}")
        print(f"  ✓ 最低价格: ¥{price_stats['min_price']:.2f}")
        print(f"  ✓ 最高价格: ¥{price_stats['max_price']:.2f}")
        
        print("\n⭐ 评分分析:")
        print(f"  ✓ 平均评分: {rating_stats['avg_rating']:.2f}")
        print(f"  ✓ 最低评分: {rating_stats['min_rating']:.2f}")
        print(f"  ✓ 最高评分: {rating_stats['max_rating']:.2f}")
    
    print("\n" + "="*70 + "\n")


def get_food_image_url(dish_name, category):
    """
    根据菜品名称获取相关图片URL
    支持多种图片源
    """
    import urllib.parse
    
    # 方案1: 使用Unsplash Source API（推荐，图片质量高）
    # 将中文菜品名转换为英文关键词
    food_keywords = {
        # 主食类
        '盖饭': 'rice bowl', '面': 'noodles', '炒饭': 'fried rice',
        '饺子': 'dumplings', '包子': 'buns', '饼': 'pancake',
        
        # 川菜
        '麻辣香锅': 'spicy hot pot', '水煮鱼': 'boiled fish', '宫保鸡丁': 'kung pao chicken',
        '麻婆豆腐': 'mapo tofu', '回锅肉': 'twice cooked pork', '鱼香肉丝': 'yuxiang pork',
        
        # 粤菜
        '白切鸡': 'white cut chicken', '烧鹅': 'roast goose', '叉烧': 'char siu',
        '虾饺': 'shrimp dumpling', '烧卖': 'shumai', '蛋挞': 'egg tart',
        
        # 素菜
        '地三鲜': 'stir fried vegetables', '豆角': 'green beans', '茄子': 'eggplant',
        '土豆丝': 'shredded potato', '西红柿': 'tomato', '鸡蛋': 'egg',
        
        # 汤羹
        '汤': 'soup', '粥': 'congee', '羹': 'thick soup',
        
        # 小吃
        '煎饼': 'pancake', '肉夹馍': 'chinese burger', '炸鸡': 'fried chicken',
        '薯条': 'french fries', '春卷': 'spring roll',
        
        # 烧烤
        '烤': 'grilled', '串': 'skewer', '羊肉串': 'lamb skewer',
        '鸡翅': 'chicken wings',
        
        # 西餐
        '牛排': 'steak', '意大利面': 'pasta', '披萨': 'pizza',
        '汉堡': 'burger', '沙拉': 'salad',
        
        # 饮品
        '奶茶': 'milk tea', '咖啡': 'coffee', '果汁': 'juice',
        '可乐': 'cola', '雪碧': 'sprite',
    }
    
    # 尝试匹配菜品名称中的关键词
    search_term = 'food'  # 默认关键词
    for keyword, english in food_keywords.items():
        if keyword in dish_name:
            search_term = english
            break
    
    # 如果没有匹配到，使用类别作为关键词
    if search_term == 'food':
        category_keywords = {
            '主食': 'asian food',
            '川菜': 'sichuan food',
            '粤菜': 'cantonese food',
            '素菜': 'vegetable dish',
            '汤羹': 'soup',
            '小吃': 'snack',
            '烧烤': 'bbq',
            '西餐': 'western food',
            '饮品': 'beverage'
        }
        search_term = category_keywords.get(category, 'chinese food')
    
    # 使用Unsplash Source API（免费，无需API key）
    # 格式: https://source.unsplash.com/800x600/?food,keyword
    encoded_term = urllib.parse.quote(search_term)
    unsplash_url = f"https://source.unsplash.com/800x600/?food,{encoded_term}"
    
    return unsplash_url, search_term


def download_images():
    """下载菜品图片（根据菜品名称匹配相关图片）"""
    try:
        import requests
        from django.core.files.base import ContentFile
    except ImportError:
        print("\n❌ 错误: 需要安装 requests 库")
        print("请运行: pip install requests")
        return
    
    print("\n开始下载菜品图片（智能匹配）...")
    
    dishes_without_image = Dish.objects.filter(image='')
    total = dishes_without_image.count()
    
    if total == 0:
        print("✓ 所有菜品都已有图片！")
        return
    
    print(f"找到 {total} 道菜品需要下载图片")
    print("注意: 使用Unsplash图片源，会根据菜品名称智能匹配相关图片\n")
    
    success_count = 0
    fail_count = 0
    matched_dishes = []
    
    for i, dish in enumerate(dishes_without_image, 1):
        # 获取菜品分类
        category = '主食'  # 默认类别
        for cat, dishes_list in CHINESE_DISHES.items():
            if dish.name in dishes_list:
                category = cat
                break
        
        # 获取匹配的图片URL
        image_url, search_term = get_food_image_url(dish.name, category)
        
        try:
            response = requests.get(image_url, timeout=15)
            response.raise_for_status()
            
            filename = f"dish_{dish.id}_{dish.name[:20]}.jpg"
            dish.image.save(filename, ContentFile(response.content), save=True)
            
            success_count += 1
            matched_dishes.append(f"{dish.name} -> {search_term}")
            
            if i % 10 == 0:
                print(f"  进度: {i}/{total} ({i/total*100:.1f}%)")
            elif i <= 5:  # 显示前5个匹配结果
                print(f"  ✓ {dish.name} -> 搜索关键词: {search_term}")
                
        except Exception as e:
            fail_count += 1
            if fail_count <= 5:
                print(f"  ✗ 失败: {dish.name} - {str(e)}")
    
    print(f"\n完成！成功: {success_count}, 失败: {fail_count}")
    
    if matched_dishes and len(matched_dishes) <= 10:
        print("\n匹配示例:")
        for match in matched_dishes[:10]:
            print(f"  {match}")
    
    print()


def generate_dishes(num_dishes_per_canteen=50, min_price=None, max_price=None):
    """生成菜品数据"""
    print("\n" + "="*70)
    print("开始生成食堂数据")
    print("="*70 + "\n")
    
    # 创建标签
    print("创建标签...")
    all_tags, tag_count = create_tags()
    print(f"  ✓ 创建/获取 {len(all_tags)} 个标签 (新增 {tag_count} 个)\n")
    
    # 获取所有餐厅
    canteens = Canteen.objects.all()
    
    if not canteens.exists():
        print("❌ 错误: 没有找到餐厅数据！")
        print("请先创建餐厅数据。")
        return
    
    print(f"找到 {canteens.count()} 个餐厅\n")
    
    # 为每个餐厅创建楼层和窗口
    print("创建楼层和窗口...")
    canteen_windows = {}
    total_floors = 0
    total_windows = 0
    
    for canteen in canteens:
        floors = create_floors_and_windows(canteen)
        windows = []
        for floor in floors:
            windows.extend(list(floor.windows.all()))
        canteen_windows[canteen.id] = windows
        print(f"  {canteen.name}: {len(floors)} 层楼, {len(windows)} 个窗口")
        total_floors += len(floors)
        total_windows += len(windows)
    
    print(f"\n  ✓ 共创建 {total_floors} 个楼层, {total_windows} 个窗口\n")
    
    # 为每个餐厅生成菜品
    total_dishes_created = 0
    
    for canteen in canteens:
        print(f"为 {canteen.name} 生成菜品...")
        
        windows = canteen_windows.get(canteen.id, [])
        if not windows:
            print(f"  ⚠️  警告: {canteen.name} 没有窗口，跳过")
            continue
        
        # 从所有菜品中随机选择
        all_available_dishes = []
        for category, dishes in CHINESE_DISHES.items():
            all_available_dishes.extend([(dish, category) for dish in dishes])
        
        random.shuffle(all_available_dishes)
        selected_dishes = all_available_dishes[:num_dishes_per_canteen]
        
        dishes_created = 0
        
        for dish_name, category in selected_dishes:
            window = random.choice(windows)
            price = generate_price(category, min_price, max_price)
            description = generate_description(dish_name, category)
            rating = generate_rating()
            view_count = random.randint(0, 500)
            
            dish, created = Dish.objects.get_or_create(
                name=dish_name,
                canteen=canteen,
                defaults={
                    'description': description,
                    'price': price,
                    'rating': rating,
                    'view_count': view_count,
                    'window': window,
                }
            )
            
            if created:
                # 添加tags（2-5个）
                num_tags = random.randint(2, 5)
                category_tags = TAG_CATEGORIES.get(category, [])
                available_tags = list(category_tags) + TAG_CATEGORIES['通用']
                selected_tag_names = random.sample(
                    available_tags,
                    min(num_tags, len(available_tags))
                )
                
                for tag_name in selected_tag_names:
                    if tag_name in all_tags:
                        dish.tags.add(all_tags[tag_name])
                
                # 添加pending_tags（0-3个，约50%的菜品有）
                if random.random() > 0.5:
                    num_pending = random.randint(1, 3)
                    pending_tag_names = random.sample(
                        available_tags,
                        min(num_pending, len(available_tags))
                    )
                    
                    for tag_name in pending_tag_names:
                        if tag_name in all_tags and tag_name not in selected_tag_names:
                            dish.pending_tags.add(all_tags[tag_name])
                
                dishes_created += 1
        
        print(f"  ✓ 创建了 {dishes_created} 道新菜品")
        total_dishes_created += dishes_created
    
    print("\n" + "="*70)
    print(f"✅ 完成！共创建 {total_dishes_created} 道菜品")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='食堂数据自动生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                              # 快速生成（每餐厅40-60道菜）
  %(prog)s -n 100                       # 每餐厅生成100道菜
  %(prog)s --clear                      # 清空现有数据并重新生成
  %(prog)s --clear-only                 # 仅清空数据，不生成新数据
  %(prog)s --stats                      # 查看数据统计
  %(prog)s --download-images            # 下载菜品图片
  %(prog)s --min-price 5 --max-price 30 # 自定义价格范围
        """
    )
    
    parser.add_argument(
        '-n', '--num-dishes',
        type=int,
        default=None,
        help='每个餐厅生成的菜品数量（默认: 40-60随机）'
    )
    
    parser.add_argument(
        '--min-price',
        type=float,
        default=None,
        help='最低价格（默认: 根据菜品类别）'
    )
    
    parser.add_argument(
        '--max-price',
        type=float,
        default=None,
        help='最高价格（默认: 根据菜品类别）'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='清空现有数据并重新生成'
    )
    
    parser.add_argument(
        '--clear-only',
        action='store_true',
        help='仅清空数据，不生成新数据'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='查看数据统计'
    )
    
    parser.add_argument(
        '--download-images',
        action='store_true',
        help='下载菜品图片'
    )
    
    args = parser.parse_args()
    
    # 仅显示统计
    if args.stats:
        show_statistics()
        return
    
    # 仅下载图片
    if args.download_images:
        download_images()
        return
    
    # 清空数据
    if args.clear or args.clear_only:
        clear_data()
        if args.clear_only:
            print("\n✅ 数据已清空\n")
            return
    
    # 生成数据
    num_dishes = args.num_dishes if args.num_dishes else random.randint(40, 60)
    
    generate_dishes(
        num_dishes_per_canteen=num_dishes,
        min_price=args.min_price,
        max_price=args.max_price
    )


if __name__ == '__main__':
    main()
