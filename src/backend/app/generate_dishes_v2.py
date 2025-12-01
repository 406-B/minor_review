"""
自动生成菜品数据脚本 V2
为每个餐厅生成楼层、窗口和大量真实的菜品数据（含图片）
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


# 将所有菜品整合到一个字典中
DISHES_BY_CATEGORY = CHINESE_DISHES


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


def create_floors_and_windows(canteen):
    """为餐厅创建楼层和窗口"""
    # 随机创建1-3层楼
    num_floors = random.randint(1, 3)
    floors = []
    
    for i in range(1, num_floors + 1):
        floor, created = Floor.objects.get_or_create(
            canteen=canteen,
            name=f"{i}楼",
            defaults={'order': i}
        )
        floors.append(floor)
        
        if created:
            # 为每层创建随机数量的窗口 (3-8个)
            num_windows = random.randint(3, 8)
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


def generate_dish_image_url(dish_name, category):
    """生成菜品图片URL（使用占位图服务）"""
    # 使用picsum.photos提供随机食物图片
    # 尺寸: 800x600
    seed = abs(hash(dish_name)) % 1000
    return f"https://picsum.photos/seed/{seed}/800/600"


def create_tags():
    """创建所有标签"""
    print("创建标签...")
    created_tags = {}
    
    for category, tags in TAG_CATEGORIES.items():
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            created_tags[tag_name] = tag
            if created:
                print(f"  创建标签: {tag_name}")
    
    print(f"共创建/获取 {len(created_tags)} 个标签")
    return created_tags


def generate_description(dish_name, category):
    """根据菜品名称和类别生成描述"""
    templates = [
        f"{dish_name}是一道经典的{category}菜品，选用优质食材，经过精心烹制而成。口感{random.choice(['鲜美', '香脆', '软糯', '嫩滑', '爽口'])}，{random.choice(['色泽诱人', '香气扑鼻', '营养丰富', '老少皆宜'])}。",
        f"精选{random.choice(['新鲜', '上等', '优质', '当季'])}食材制作的{dish_name}，{random.choice(['传统工艺', '独家秘方', '精心调制', '匠心烹饪'])}，{random.choice(['味道鲜美', '口感绝佳', '回味无穷', '深受好评'])}。",
        f"{dish_name}采用{random.choice(['传统', '现代', '创新', '特色'])}烹饪技法，{random.choice(['保留了食材的原汁原味', '完美融合多种风味', '营养与美味兼具', '是本餐厅的招牌菜品之一'])}。",
        f"这道{dish_name}{random.choice(['色香味俱全', '深受食客喜爱', '是本店特色', '广受好评'])}，{random.choice(['适合各个年龄段', '营养均衡', '健康美味', '物美价廉'])}，值得品尝。"
    ]
    
    description = random.choice(templates)
    
    # 添加一些额外的细节
    details = [
        f"每份{random.choice(['分量足', '精致小巧', '适中', '超大份'])}。",
        f"{random.choice(['推荐搭配米饭食用', '可单独享用', '适合多人分享', '是下饭的好选择'])}。",
        f"{random.choice(['本店畅销菜品', '厨师推荐', '顾客最爱', '必点菜品'])}。"
    ]
    
    if random.random() > 0.5:
        description += " " + random.choice(details)
    
    return description


def generate_price(category):
    """根据类别生成合理的价格"""
    price_ranges = {
        '主食': (8, 18),
        '川菜': (12, 28),
        '粤菜': (15, 35),
        '素菜': (6, 15),
        '汤羹': (5, 12),
        '小吃': (5, 15),
        '烧烤': (2, 8),  # 单串价格
        '西餐': (20, 45),
        '饮品': (5, 15)
    }
    
    min_price, max_price = price_ranges.get(category, (8, 20))
    price = round(random.uniform(min_price, max_price), 1)
    return Decimal(str(price))


def generate_rating():
    """生成评分 (3.5-5.0之间)"""
    rating = round(random.uniform(3.5, 5.0), 2)
    return Decimal(str(rating))


def main():
    print("="*70)
    print("开始生成菜品数据 V2")
    print("="*70)
    print()
    
    # 创建标签
    all_tags = create_tags()
    print()
    
    # 获取所有餐厅
    canteens = Canteen.objects.all()
    
    if not canteens.exists():
        print("错误: 没有找到餐厅数据！")
        print("请先创建餐厅数据。")
        return
    
    print(f"找到 {canteens.count()} 个餐厅")
    print()
    
    # 为每个餐厅创建楼层和窗口
    print("创建楼层和窗口...")
    canteen_windows = {}
    for canteen in canteens:
        floors = create_floors_and_windows(canteen)
        # 收集所有窗口
        windows = []
        for floor in floors:
            windows.extend(list(floor.windows.all()))
        canteen_windows[canteen.id] = windows
        print(f"  {canteen.name}: {len(floors)} 层楼, {len(windows)} 个窗口")
    print()
    
    total_dishes_created = 0
    
    # 为每个餐厅生成菜品
    for canteen in canteens:
        print(f"为 {canteen.name} 生成菜品...")
        
        # 获取该餐厅的所有窗口
        windows = canteen_windows.get(canteen.id, [])
        if not windows:
            print(f"  警告: {canteen.name} 没有窗口，跳过")
            continue
        
        # 每个餐厅随机生成40-60道菜
        num_dishes = random.randint(40, 60)
        dishes_created = 0
        
        # 从所有菜品中随机选择
        all_available_dishes = []
        for category, dishes in DISHES_BY_CATEGORY.items():
            all_available_dishes.extend([(dish, category) for dish in dishes])
        
        # 打乱顺序并选择指定数量
        random.shuffle(all_available_dishes)
        selected_dishes = all_available_dishes[:num_dishes]
        
        for dish_name, category in selected_dishes:
            # 随机分配窗口
            window = random.choice(windows)
            
            # 生成价格（根据类别）
            price = generate_price(category)
            
            # 生成描述
            description = generate_description(dish_name, category)
            
            # 生成图片URL
            image_url = generate_dish_image_url(dish_name, category)
            
            # 生成评分
            rating = generate_rating()
            
            # 生成浏览次数
            view_count = random.randint(0, 500)
            
            # 创建菜品（注意：这里我们不直接保存image字段，因为它是ImageField）
            # 我们将在后面通过其他方式处理图片
            dish, created = Dish.objects.get_or_create(
                name=dish_name,
                canteen=canteen,
                defaults={
                    'description': description,
                    'price': price,
                    'rating': rating,
                    'view_count': view_count,
                    'window': window,
                    # image字段留空，需要真实上传图片文件
                }
            )
            
            if created:
                # 添加tags（2-5个）
                num_tags = random.randint(2, 5)
                category_tags = TAG_CATEGORIES.get(category, [])
                
                # 从该类别和通用标签中选择
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
                
                # 打印图片URL信息（供参考）
                if dishes_created <= 3:  # 只打印前3个
                    print(f"    {dish_name}: {image_url}")
        
        print(f"  创建了 {dishes_created} 道新菜品")
        total_dishes_created += dishes_created
    
    print()
    print("="*70)
    print(f"完成！共创建 {total_dishes_created} 道菜品")
    print()
    print("注意：图片字段使用的是占位图URL，实际部署时需要:")
    print("  1. 下载真实菜品图片")
    print("  2. 使用Django的ImageField上传")
    print("  3. 或者修改模型使用URLField存储图片链接")
    print("="*70)


if __name__ == '__main__':
    main()
