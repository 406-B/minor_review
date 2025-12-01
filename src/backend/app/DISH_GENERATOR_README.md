# 菜品数据自动生成工具

## 📖 功能说明

本工具可以自动为食堂数据库生成大量真实的菜品数据，包括：
- ✅ 菜品名称（涵盖9大类别，共200+道菜）
- ✅ 详细描述（智能生成，包含食材、烹饪方法、口感等）
- ✅ 合理价格（根据菜品类别自动定价）
- ✅ 评分（3.5-5.0分）
- ✅ 标签系统（口味、特色、饮食习惯等7大类60+标签）
- ✅ Pending Tags（模拟用户提交的待审核标签）
- ✅ 浏览量（模拟真实数据）

## 📁 文件说明

### 1. `generate_dishes.py` - 基础生成脚本
最简单的生成脚本，适合快速生成数据。

**特点:**
- 自动为每个餐厅生成菜品
- 每个类别默认生成5道菜
- 自动创建所有标签
- 智能匹配菜品与标签

**使用方法:**
```bash
cd src/backend/app
python generate_dishes.py
```

### 2. `batch_generate_dishes.py` - 高级批量生成
支持更多自定义选项的高级脚本。

**特点:**
- 支持自定义每个餐厅生成的菜品数量
- 支持自定义价格范围
- 可以清空现有数据
- 提供数据统计功能

**使用方法:**

```bash
# 基本用法：每个餐厅生成50道菜
python batch_generate_dishes.py

# 自定义数量：每个餐厅生成100道菜
python batch_generate_dishes.py -n 100

# 清空现有数据并重新生成
python batch_generate_dishes.py --clear

# 仅查看统计信息
python batch_generate_dishes.py --stats

# 自定义价格范围
python batch_generate_dishes.py --min-price 3.0 --max-price 50.0

# 组合使用
python batch_generate_dishes.py -n 80 --clear --min-price 5.0 --max-price 35.0
```

**参数说明:**
- `-n, --number`: 每个餐厅生成的菜品数量（默认50）
- `--clear`: 清空现有菜品数据
- `--stats`: 仅显示数据库统计信息
- `--min-price`: 最低价格（默认5.0）
- `--max-price`: 最高价格（默认30.0）

## 🍽️ 菜品分类

生成的菜品涵盖以下类别：

1. **主食类** (27道)
   - 盖饭系列、面食系列、炒饭系列、面点系列

2. **川菜类** (18道)
   - 麻辣香锅、水煮鱼、宫保鸡丁等经典川菜

3. **粤菜类** (19道)
   - 白切鸡、烧鹅、点心等粤式美食

4. **素菜类** (19道)
   - 各类时令蔬菜、豆制品菜肴

5. **汤羹类** (15道)
   - 各式汤品、粥类

6. **小吃类** (27道)
   - 传统小吃、油炸小食

7. **烧烤类** (18道)
   - 各类烧烤串、烤蔬菜

8. **西餐类** (15道)
   - 意面、披萨、汉堡、牛排等

9. **饮品类** (20道)
   - 豆浆、奶茶、果汁、咖啡等

**总计:** 200+ 道不同菜品

## 🏷️ 标签系统

自动创建60+个标签，分为7大类：

1. **口味标签**: 麻辣、酸辣、香辣、清淡、鲜香、甜味等
2. **特色标签**: 招牌菜、人气推荐、新品上市、限时特惠等
3. **饮食习惯**: 素食、清真、无辣、低脂、低糖、高蛋白等
4. **烹饪方式**: 现炒、清蒸、红烧、煎炸、烧烤等
5. **餐次标签**: 早餐、午餐、晚餐、夜宵、下午茶
6. **食材标签**: 牛肉、猪肉、鸡肉、海鲜、豆制品等
7. **营养标签**: 高蛋白、低卡路里、富含维生素等

标签会根据菜品名称和类别**智能匹配**。

## 📊 生成效果示例

假设数据库有10个餐厅，使用默认配置：

```
餐厅总数: 10
菜品总数: ~400道 (每个餐厅约40道)
标签总数: 60+
平均每餐厅: 40道菜
价格范围: ¥2.0 - ¥35.0
评分范围: 3.50 - 5.00
```

每道菜品包含：
- ✅ 名称: "宫保鸡丁盖饭"
- ✅ 描述: 约100-150字的详细描述
- ✅ 价格: ¥12.5
- ✅ 评分: 4.35
- ✅ 标签: [麻辣, 鸡肉, 主食, 招牌菜, 现炒]
- ✅ Pending Tags: [高蛋白, 午餐] (随机)
- ✅ 浏览量: 125次

## 🔧 使用流程

### 第一次使用

```bash
# 1. 进入后端目录
cd src/backend/app

# 2. 运行生成脚本（基础版）
python generate_dishes.py
```

### 定制化生成

```bash
# 1. 先查看当前数据统计
python batch_generate_dishes.py --stats

# 2. 清空数据并生成100道菜/餐厅
python batch_generate_dishes.py -n 100 --clear

# 3. 再次查看统计
python batch_generate_dishes.py --stats
```

### 增量添加

```bash
# 不使用 --clear 参数，直接添加更多菜品
python batch_generate_dishes.py -n 50
```

## 💡 高级技巧

### 1. 生成大量数据用于测试

```bash
# 每个餐厅生成200道菜
python batch_generate_dishes.py -n 200 --clear
```

### 2. 生成特定价格区间的菜品

```bash
# 生成高端菜品（价格20-80元）
python batch_generate_dishes.py --min-price 20.0 --max-price 80.0

# 生成经济型菜品（价格3-15元）
python batch_generate_dishes.py --min-price 3.0 --max-price 15.0
```

### 3. 在Python代码中使用

```python
from batch_generate_dishes import generate_batch

# 程序化生成
generate_batch(
    dishes_per_canteen=100,
    min_price=5.0,
    max_price=30.0,
    clear_data=True
)
```

## ⚠️ 注意事项

1. **数据库要求**: 确保数据库中已有餐厅数据
2. **清空操作**: 使用 `--clear` 参数会删除所有现有菜品，请谨慎使用
3. **生成时间**: 生成大量数据可能需要几分钟，请耐心等待
4. **标签创建**: 首次运行会自动创建所有标签
5. **图片字段**: 当前版本不生成实际图片文件，image字段为空

## 📈 性能建议

- **小型测试**: 每个餐厅20-30道菜
- **正常使用**: 每个餐厅50-80道菜
- **大规模测试**: 每个餐厅100-200道菜

## 🔍 数据验证

生成后可以通过Django Admin或API验证：

```bash
# 启动Django shell
python manage.py shell

# 查询菜品
from list.models import Dish, Canteen, Tag

# 查看总数
print(f"菜品总数: {Dish.objects.count()}")
print(f"餐厅总数: {Canteen.objects.count()}")
print(f"标签总数: {Tag.objects.count()}")

# 查看某个餐厅的菜品
canteen = Canteen.objects.first()
dishes = canteen.dishes.all()
for dish in dishes[:5]:
    print(f"{dish.name} - ¥{dish.price} - {dish.rating}分")
```

## 🎯 常见问题

**Q: 为什么有些餐厅菜品数量不一样？**
A: 这是正常的，因为从每个类别随机选择菜品，某些类别可能菜品较少。

**Q: 可以修改菜品名称吗？**
A: 可以！编辑 `generate_dishes.py` 中的 `CHINESE_DISHES` 字典添加自己的菜品。

**Q: 如何添加新的标签类别？**
A: 编辑 `TAG_CATEGORIES` 字典，添加新的类别和标签即可。

**Q: 能否生成图片？**
A: 当前版本不生成图片。如需图片，可以手动上传或使用其他工具批量下载。

## 📝 自定义扩展

### 添加新菜品

编辑 `generate_dishes.py`，在 `CHINESE_DISHES` 字典中添加：

```python
CHINESE_DISHES = {
    '主食': [...],
    '新类别': [
        '菜品1', '菜品2', '菜品3'
    ]
}
```

### 修改描述模板

编辑 `DESCRIPTIONS` 列表添加新的描述模板：

```python
DESCRIPTIONS = [
    '你的新模板: {special}{texture}...',
    ...
]
```

### 调整价格范围

修改 `generate_price()` 函数中的 `price_ranges` 字典。

## 📞 支持

如有问题，请查看代码注释或联系开发团队。

---

**最后更新**: 2024-12-01  
**版本**: 1.0.0
