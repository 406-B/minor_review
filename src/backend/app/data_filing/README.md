# 食堂数据自动生成工具

## 📖 简介

这是一个全功能的食堂数据自动生成工具，可以为数据库中的餐厅自动创建完整的数据结构，包括楼层、窗口和菜品信息。

## ✨ 功能特性

- ✅ **自动创建楼层**：每个餐厅1-3层楼
- ✅ **自动创建窗口**：每层楼3-8个窗口，支持数字编号和特色命名
- ✅ **批量生成菜品**：200+道中式菜品，涵盖9大类别
- ✅ **智能标签系统**：60+个标签，自动匹配菜品类别
- ✅ **合理价格区间**：根据菜品类别智能定价
- ✅ **数据统计功能**：查看生成数据的详细统计信息
- ✅ **图片下载功能**：从占位图服务下载菜品图片
- ✅ **数据清理功能**：支持清空现有数据
- ✅ **灵活参数配置**：支持自定义生成数量、价格范围等

## 🚀 快速开始

### 基础使用

```bash
cd src/backend/app/data_filing
python generate_canteen_data.py
```

这将为每个餐厅生成40-60道菜（随机数量），并自动创建楼层和窗口。

### 常用命令

```bash
# 1. 查看当前数据统计
python generate_canteen_data.py --stats

# 2. 清空所有数据（不生成新数据）
python generate_canteen_data.py --clear-only

# 3. 清空并重新生成数据
python generate_canteen_data.py --clear

# 4. 指定每个餐厅生成100道菜
python generate_canteen_data.py -n 100

# 5. 下载菜品图片
python generate_canteen_data.py --download-images

# 6. 自定义价格范围（5-30元）
python generate_canteen_data.py --min-price 5 --max-price 30

# 7. 组合使用：清空数据，生成50道菜，价格10-25元
python generate_canteen_data.py --clear -n 50 --min-price 10 --max-price 25
```

## 📚 参数说明

### 必选参数
无（所有参数都是可选的）

### 可选参数

| 参数 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--num-dishes` | `-n` | 整数 | 40-60（随机） | 每个餐厅生成的菜品数量 |
| `--min-price` | - | 浮点数 | 根据类别 | 菜品最低价格（元） |
| `--max-price` | - | 浮点数 | 根据类别 | 菜品最高价格（元） |
| `--clear` | - | 标志 | False | 清空现有数据并重新生成 |
| `--clear-only` | - | 标志 | False | 仅清空数据，不生成新数据 |
| `--stats` | - | 标志 | False | 查看数据统计 |
| `--download-images` | - | 标志 | False | 下载菜品图片 |

## 📊 生成数据详情

### 楼层（Floor）
- **数量**：每个餐厅1-3层（随机）
- **命名**：1楼、2楼、3楼
- **排序**：按楼层号自动排序

### 窗口（Window）
- **数量**：每层3-8个（随机）
- **命名方式**：
  - 数字编号：1号窗口、2号窗口...
  - 特色名称：川菜窗口、粤菜窗口、面食窗口...
- **分布**：自动关联到所属楼层

### 菜品类别（9大类）

| 类别 | 菜品数 | 默认价格范围 | 示例菜品 |
|------|--------|--------------|----------|
| 主食 | 35道 | ¥8-18 | 红烧肉盖饭、炸酱面、扬州炒饭 |
| 川菜 | 18道 | ¥12-28 | 麻辣香锅、水煮鱼、宫保鸡丁 |
| 粤菜 | 18道 | ¥15-35 | 白切鸡、烧鹅、虾饺 |
| 素菜 | 18道 | ¥6-15 | 地三鲜、干煸四季豆、清炒油麦菜 |
| 汤羹 | 15道 | ¥5-12 | 紫菜蛋花汤、玉米排骨汤 |
| 小吃 | 20道 | ¥5-15 | 煎饼果子、炸鸡、锅贴 |
| 烧烤 | 17道 | ¥2-8 | 羊肉串、烤鸡翅、烤茄子 |
| 西餐 | 20道 | ¥20-45 | 牛排、意大利面、披萨 |
| 饮品 | 20道 | ¥5-15 | 珍珠奶茶、咖啡、果汁 |

### 标签系统（60+标签）

**分类**：
- 口味类：麻辣、香辣、清淡、酸甜等
- 烹饪类：蒸菜、烤串、炒菜、凉拌等
- 特色类：热销、推荐、新品、经典等
- 健康类：素菜、营养、养生等
- 菜系类：川菜、粤菜、西餐等
- 餐次类：午餐、晚餐、夜宵等
- 其他：份量足、实惠、适合分享等

**使用规则**：
- 每道菜自动添加2-5个相关标签
- 约50%的菜品有1-3个待审核标签（pending tags）

### 其他数据

- **评分**：3.5-5.0分（随机生成）
- **浏览量**：0-500次（随机生成）
- **描述**：智能生成，包含食材、烹饪方法、口感等信息

## 💡 使用场景

### 场景1：首次部署
```bash
# 查看当前状态
python generate_canteen_data.py --stats

# 生成初始数据（每餐厅50道菜）
python generate_canteen_data.py -n 50

# 下载图片
python generate_canteen_data.py --download-images
```

### 场景2：开发测试
```bash
# 快速生成少量数据用于测试
python generate_canteen_data.py -n 20

# 需要重新测试时清空并重新生成
python generate_canteen_data.py --clear -n 20
```

### 场景3：生产环境
```bash
# 清空测试数据
python generate_canteen_data.py --clear-only

# 生成大量真实数据
python generate_canteen_data.py -n 100 --min-price 8 --max-price 50

# 下载真实图片
python generate_canteen_data.py --download-images
```

### 场景4：数据维护
```bash
# 查看数据统计
python generate_canteen_data.py --stats

# 仅补充新菜品（不清空）
python generate_canteen_data.py -n 30
```

## 🔧 高级配置

### 修改楼层数量范围
编辑 `generate_canteen_data.py` 第146行：
```python
def create_floors_and_windows(canteen, min_floors=1, max_floors=3, ...):
    # 修改 max_floors 参数，例如改为5表示最多5层
```

### 修改窗口数量范围
编辑 `generate_canteen_data.py` 第146行：
```python
def create_floors_and_windows(canteen, ..., min_windows=3, max_windows=8):
    # 修改 min_windows 和 max_windows 参数
```

### 添加自定义菜品
编辑 `generate_canteen_data.py` 第33-123行的 `CHINESE_DISHES` 字典：
```python
CHINESE_DISHES = {
    '主食': [
        '红烧肉盖饭',
        '你的新菜品',  # 添加这里
        ...
    ],
    # 或者添加新类别
    '新类别': ['菜品1', '菜品2', ...]
}
```

### 添加自定义标签
编辑 `generate_canteen_data.py` 第127-143行的 `TAG_CATEGORIES` 字典：
```python
TAG_CATEGORIES = {
    '通用': [
        '热销',
        '你的新标签',  # 添加这里
        ...
    ],
}
```

## 🖼️ 图片处理（智能匹配）

### 图片匹配逻辑 ⭐

脚本使用 **智能关键词匹配** 系统，根据菜品名称下载相关图片：

**工作原理：**
1. 分析菜品名称，提取关键词（如"可乐"→"cola"，"牛排"→"steak"）
2. 使用Unsplash Source API搜索相关食物图片
3. 下载并保存到 `media/dishes/` 目录

**匹配示例：**
- 🥤 可乐 → 搜索关键词: "cola"
- 🥩 牛排 → 搜索关键词: "steak"  
- 🍜 炸酱面 → 搜索关键词: "noodles"
- 🍗 宫保鸡丁 → 搜索关键词: "kung pao chicken"
- 🧋 珍珠奶茶 → 搜索关键词: "milk tea"
- 🍕 披萨 → 搜索关键词: "pizza"

**支持的关键词库：**
- 60+ 中文→英文菜品关键词映射
- 9大类别通用关键词
- 智能回退机制（未匹配时使用类别关键词）

### 方案1：智能匹配图片（推荐）

```bash
# 1. 安装依赖
pip install requests

# 2. 下载匹配图片
python generate_canteen_data.py --download-images
```

**优点：**
- ✅ 图片与菜品名称相关
- ✅ 高质量图片（来自Unsplash）
- ✅ 免费，无需API key
- ✅ 自动匹配60+常见菜品

**输出示例：**
```
开始下载菜品图片（智能匹配）...
找到 500 道菜品需要下载图片

  ✓ 可乐 -> 搜索关键词: cola
  ✓ 牛排 -> 搜索关键词: steak
  ✓ 宫保鸡丁 -> 搜索关键词: kung pao chicken
  进度: 10/500 (2.0%)
  ...

完成！成功: 495, 失败: 5
```

### 方案2：使用占位图（开发测试）

如果只是开发测试，可以不下载图片，前端使用占位图URL：
```javascript
// 前端代码示例
const placeholderUrl = `https://source.unsplash.com/800x600/?food,${dishCategory}`;
```

### 方案3：修改为URLField

如果想直接存储图片URL而不是文件：

1. 修改 `list/models.py` 中的Dish模型：
```python
# 将
image = models.ImageField(upload_to='dishes/', ...)
# 改为
image = models.URLField(blank=True, null=True, ...)
```

2. 执行迁移：
```bash
python manage.py makemigrations
python manage.py migrate
```

### 扩展关键词库

如果想添加更多菜品的关键词映射，编辑 `generate_canteen_data.py` 第267行：

```python
food_keywords = {
    # 添加你的菜品映射
    '你的菜品名': 'english keyword',
    '糖醋排骨': 'sweet and sour pork',
    '小龙虾': 'crayfish',
    # ...
}
```

## 📈 数据统计示例

运行 `python generate_canteen_data.py --stats` 输出示例：

```
======================================================================
数据统计报告
======================================================================

📊 基础数据:
  ✓ 餐厅数量: 10
  ✓ 菜品总数: 487
  ✓ 标签总数: 65
  ✓ 楼层总数: 18
  ✓ 窗口总数: 95
  ✓ 平均每餐厅: 48.7 道菜
  ✓ 平均每餐厅: 1.8 层楼
  ✓ 平均每餐厅: 9.5 个窗口

💰 价格分析:
  ✓ 平均价格: ¥14.23
  ✓ 最低价格: ¥2.50
  ✓ 最高价格: ¥42.80

⭐ 评分分析:
  ✓ 平均评分: 4.31
  ✓ 最低评分: 3.52
  ✓ 最高评分: 4.99

======================================================================
```

## ❓ 常见问题

### Q1: 运行脚本提示找不到模块？
**A:** 确保在正确的目录下运行：
```bash
cd src/backend/app/data_filing
python generate_canteen_data.py
```

### Q2: 菜品没有分配到窗口？
**A:** 脚本会自动为每个餐厅创建楼层和窗口，并将菜品分配到窗口。如果出现此问题，可能是数据不一致，建议使用 `--clear` 参数重新生成。

### Q3: 想要固定数量的菜品而不是随机数量？
**A:** 使用 `-n` 参数指定固定数量：
```bash
python generate_canteen_data.py -n 50
```

### Q4: 如何只清空菜品但保留楼层和窗口？
**A:** 当前版本的 `--clear-only` 会清空所有数据。如需仅清空菜品，可以使用Django shell：
```bash
python manage.py shell
>>> from list.models import Dish
>>> Dish.objects.all().delete()
```

### Q5: 下载图片很慢或失败？
**A:** 
- 检查网络连接
- 可能是占位图服务限流，稍后重试
- 或者不下载图片，使用占位图URL

### Q6: 可以为已有的餐厅补充菜品吗？
**A:** 可以！不使用 `--clear` 参数，脚本会在现有数据基础上添加新菜品（如果菜品名称不重复）。

### Q7: 生成的菜品重复了？
**A:** 脚本使用 `get_or_create` 避免重复。如果同一餐厅出现同名菜品，不会重复创建。

## 🛠️ 技术实现

- **Django ORM**：使用 `get_or_create` 避免重复数据
- **随机化**：每个餐厅的菜品、楼层、窗口都是随机生成
- **关联关系**：自动建立菜品↔餐厅、菜品↔窗口、菜品↔标签的多对多/外键关联
- **数据验证**：价格、评分都有合理范围限制
- **命令行参数**：使用 `argparse` 提供灵活的CLI接口

## 📝 文件结构

```
data_filing/
├── README.md                    # 本文档
└── generate_canteen_data.py     # 主程序（全功能集成）
```

## 🔄 工作流程

```
开始
  ↓
解析命令行参数
  ↓
[--stats] → 显示统计 → 结束
  ↓
[--download-images] → 下载图片 → 结束
  ↓
[--clear/--clear-only] → 清空数据
  ↓
[--clear-only] → 结束
  ↓
创建标签
  ↓
为每个餐厅创建楼层和窗口
  ↓
为每个餐厅生成菜品
  ↓
显示完成信息
  ↓
结束
```

## 📞 支持

如遇问题，请检查：
1. Django环境是否正确配置
2. 数据库中是否有餐厅数据
3. 运行目录是否正确
4. 命令行参数是否正确

---

**祝使用愉快！** 🎉

如有任何问题或建议，欢迎反馈！
