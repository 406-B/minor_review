# 菜品数据自动生成工具 V2

## 📖 功能说明

本工具可以自动为食堂数据库生成完整的餐厅结构和菜品数据，包括：
- ✅ **楼层和窗口**（每个餐厅1-3层楼，每层3-8个窗口）
- ✅ **菜品名称**（涵盖9大类别，共200+道菜）
- ✅ **详细描述**（智能生成，包含食材、烹饪方法、口感等）
- ✅ **合理价格**（根据菜品类别自动定价）
- ✅ **菜品图片**（支持占位图或真实下载）
- ✅ **评分**（3.5-5.0分）
- ✅ **标签系统**（口味、特色、饮食习惯等7大类60+标签）
- ✅ **Pending Tags**（模拟用户提交的待审核标签）
- ✅ **浏览量**（模拟真实数据）

## 🚀 快速开始

### Windows用户（推荐）
双击运行：`quick_generate.bat`

### Linux/macOS用户（推荐）
```bash
chmod +x quick_generate.sh
./quick_generate.sh
```

## 📁 文件说明

### 1. `generate_dishes_v2.py` - 完整版生成脚本 ⭐推荐
**新版本！**包含楼层、窗口和菜品的完整生成。

**特点:**
- ✅ 自动为每个餐厅创建1-3层楼层
- ✅ 每层楼创建3-8个随机窗口
- ✅ 菜品自动分配到窗口
- ✅ 每个餐厅生成40-60道菜
- ✅ 自动创建所有标签
- ✅ 智能匹配菜品与标签

**使用方法:**
```bash
cd src/backend/app
python generate_dishes_v2.py
```

### 2. `download_dish_images.py` - 图片下载工具
为菜品下载真实图片（从占位图服务）。

**特点:**
- 自动下载所有缺少图片的菜品
- 保存到Django的media目录
- 显示下载进度

**使用方法:**
```bash
cd src/backend/app
pip install requests  # 如果还没安装
python download_dish_images.py
```

**注意：** 需要先安装requests库：`pip install requests`

### 3. `validate_dishes.py` - 数据验证工具
验证生成的数据完整性和合理性。

**功能:**
- 📊 数据统计（菜品数、餐厅数、标签数、楼层数、窗口数）
- 💰 价格分析
- ⭐ 评分分布
- 🏷️ 标签使用情况
- 📍 各餐厅详情（包含楼层和窗口统计）
- 🔍 数据完整性检查
- 🌟 推荐菜品展示

**使用方法:**
```bash
# 查看完整报告
python validate_dishes.py

# 查看样本菜品
python validate_dishes.py --sample
```

### 4. `quick_generate.bat` / `quick_generate.sh` - 交互式菜单
最用户友好的生成工具，提供交互式菜单。

**功能菜单:**
1. 快速生成（推荐）- 每餐厅50道菜
2. 大量生成 - 每餐厅100道菜
3. 小量生成 - 每餐厅20道菜
4. 清空并重新生成
5. 查看数据统计
6. 自定义生成

## 📝 使用流程

### 完整流程（推荐）

```bash
cd src/backend/app

# 步骤1: 生成楼层、窗口和菜品
python generate_dishes_v2.py

# 步骤2: 验证数据
python validate_dishes.py

# 步骤3（可选）: 下载真实图片
# 注意：这会从网络下载图片，需要时间
pip install requests
python download_dish_images.py

# 步骤4: 再次验证
python validate_dishes.py
```

### 快速流程

```bash
# Windows用户
quick_generate.bat

# Linux/macOS用户
chmod +x quick_generate.sh
./quick_generate.sh
```

## 🎯 数据结构

### 楼层（Floor）
- 每个餐厅：1-3层楼
- 命名：1楼、2楼、3楼
- 排序：按楼层号

### 窗口（Window）
- 每层楼：3-8个窗口
- 命名：数字编号或特色名称
  - 1号窗口、2号窗口...
  - 川菜窗口、粤菜窗口...
- 排序：按创建顺序

### 菜品类别（9大类）
- **主食**: 盖饭、面条、炒饭等 (35道)
- **川菜**: 麻辣、水煮、干锅等 (18道)
- **粤菜**: 烧味、蒸菜、点心等 (18道)
- **素菜**: 各类蔬菜炒菜 (18道)
- **汤羹**: 各种汤和粥 (15道)
- **小吃**: 油炸小食、街边小吃 (20道)
- **烧烤**: 各类烤串 (17道)
- **西餐**: 牛排、意面、披萨等 (20道)
- **饮品**: 奶茶、果汁、咖啡等 (20道)

### 价格范围
- 主食: ¥8-18
- 川菜: ¥12-28
- 粤菜: ¥15-35
- 素菜: ¥6-15
- 汤羹: ¥5-12
- 小吃: ¥5-15
- 烧烤: ¥2-8（单串）
- 西餐: ¥20-45
- 饮品: ¥5-15

### 标签系统（7大类，60+标签）
- **口味类**: 麻辣、香辣、清淡、酸甜等
- **烹饪类**: 蒸菜、烤串、炒菜、凉拌等
- **特色类**: 热销、推荐、新品、经典等
- **健康类**: 素菜、营养、养生、低脂等
- **菜系类**: 川菜、粤菜、西餐等
- **餐次类**: 午餐、晚餐、夜宵等
- **其他**: 份量足、实惠、适合分享等

## 🔧 自定义配置

### 修改生成数量
编辑 `generate_dishes_v2.py`:
```python
# 第302行附近
num_dishes = random.randint(40, 60)  # 改为你想要的范围
```

### 修改楼层数量
编辑 `generate_dishes_v2.py`:
```python
# 第148行附近
num_floors = random.randint(1, 3)  # 改为你想要的范围，如(1, 4)为1-4层
```

### 修改窗口数量
编辑 `generate_dishes_v2.py`:
```python
# 第159行附近
num_windows = random.randint(3, 8)  # 改为你想要的范围
```

### 修改价格范围
编辑 `generate_dishes_v2.py` 的 `generate_price` 函数:
```python
price_ranges = {
    '主食': (8, 18),  # 改为你想要的价格范围
    ...
}
```

## 🖼️ 关于图片

### 选项1：使用占位图（默认，推荐用于开发）
脚本默认生成占位图URL，不占用本地存储，适合开发测试。

图片格式：`https://picsum.photos/seed/{唯一种子}/800/600`

### 选项2：下载真实图片（推荐用于生产）
```bash
pip install requests
python download_dish_images.py
```

这会从占位图服务下载图片并保存到 `media/dishes/` 目录。

### 选项3：修改为URLField
如果想存储图片URL而不是文件，修改模型：
```python
# list/models.py
image = models.URLField(blank=True, null=True, help_text="Dish photo URL")
```

然后运行：
```bash
python manage.py makemigrations
python manage.py migrate
```

## ❓ 常见问题

### Q: 生成的菜品没有图片？
**A:** 有两种解决方案：
1. 运行 `python download_dish_images.py` 下载图片（需要安装requests）
2. 修改Dish模型的image字段为URLField（见上文"选项3"）

### Q: 如何清空现有数据？
**A:** 使用交互式菜单的"清空并重新生成"选项，或在Django shell中：
```python
python manage.py shell
>>> from list.models import Dish, Tag, Floor, Window
>>> Dish.objects.all().delete()
>>> Tag.objects.all().delete()
>>> Floor.objects.all().delete()
>>> Window.objects.all().delete()
```

### Q: 生成的菜品数量不够？
**A:** 编辑脚本修改范围，或使用批量生成工具指定数量。

### Q: 窗口和楼层已存在会怎样？
**A:** 脚本使用 `get_or_create`，不会重复创建，会复用现有的楼层和窗口。

### Q: 下载图片失败？
**A:** 可能是网络问题，可以：
1. 检查网络连接
2. 使用代理
3. 稍后重试
4. 或者不下载图片，使用占位图URL

### Q: 菜品分配到窗口有规则吗？
**A:** 当前是随机分配，如需按类别分配，可修改脚本添加规则。

## 📊 示例输出

```
======================================================================
开始生成菜品数据 V2
======================================================================

创建标签...
  创建标签: 主食
  创建标签: 川菜
  ...
共创建/获取 65 个标签

找到 10 个餐厅

创建楼层和窗口...
  食堂1: 2 层楼, 11 个窗口
  食堂2: 3 层楼, 16 个窗口
  ...

为 食堂1 生成菜品...
    红烧肉盖饭: https://picsum.photos/seed/123/800/600
    宫保鸡丁盖饭: https://picsum.photos/seed/456/800/600
    麻婆豆腐盖饭: https://picsum.photos/seed/789/800/600
  创建了 45 道新菜品

为 食堂2 生成菜品...
  创建了 52 道新菜品

...

======================================================================
完成！共创建 487 道菜品

注意：图片字段使用的是占位图URL，实际部署时需要:
  1. 下载真实菜品图片
  2. 使用Django的ImageField上传
  3. 或者修改模型使用URLField存储图片链接
======================================================================
```

## 🎓 技术细节

- **Django ORM**: 使用 `get_or_create` 避免重复数据
- **随机化**: 每个餐厅的菜品、标签都是随机选择
- **关联关系**: 自动建立菜品-餐厅、菜品-窗口、菜品-标签的关联
- **数据验证**: 价格、评分都有合理的范围限制
- **图片处理**: 支持ImageField和URLField两种方式

## 📞 支持

如有问题，请查看：
1. Django日志
2. `validate_dishes.py` 的输出
3. 数据库中的实际数据

---

**祝使用愉快！** 🎉
