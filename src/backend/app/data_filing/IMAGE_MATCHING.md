# 图片智能匹配系统说明

## 🎯 问题背景

**用户需求：** "可乐就需要可乐的图片，怎么才能做到？"

**核心挑战：** 如何让下载的图片内容与菜品名称匹配？

## 💡 解决方案

### 系统原理

采用 **中文→英文关键词映射 + Unsplash图片搜索** 的方案：

```
菜品名称 → 提取关键词 → 翻译成英文 → 搜索图片 → 下载保存
   ↓
  可乐  →    可乐     →   cola    →  🥤图片  →  保存
```

### 关键词库

#### 1. 直接匹配（60+菜品）

```python
'可乐': 'cola'              # 🥤 可乐 → cola图片
'牛排': 'steak'             # 🥩 牛排 → 牛排图片
'宫保鸡丁': 'kung pao chicken'  # 🍗 宫保鸡丁 → 宫保鸡丁图片
'珍珠奶茶': 'milk tea'       # 🧋 奶茶 → 奶茶图片
'炸酱面': 'noodles'         # 🍜 炸酱面 → 面条图片
'披萨': 'pizza'             # 🍕 披萨 → 披萨图片
```

#### 2. 模糊匹配（关键词包含）

```python
# 如果菜品名包含关键词，使用该关键词
'红烧肉盖饭' → 包含'盖饭' → 'rice bowl'
'牛肉拉面'   → 包含'面'   → 'noodles'
'炸鸡腿'     → 包含'鸡'   → 'chicken'
```

#### 3. 类别回退

如果没有匹配到关键词，使用菜品类别：

```python
川菜 → 'sichuan food'
粤菜 → 'cantonese food'
西餐 → 'western food'
饮品 → 'beverage'
```

## 📊 匹配效果

### 示例1: 饮品类

| 菜品名 | 搜索关键词 | 预期图片内容 |
|--------|-----------|-------------|
| 可乐 | cola | 🥤 可乐瓶/可乐杯 |
| 雪碧 | sprite | 🥤 雪碧饮料 |
| 珍珠奶茶 | milk tea | 🧋 奶茶杯 |
| 咖啡 | coffee | ☕ 咖啡 |
| 橙汁 | juice | 🧃 橙汁 |

### 示例2: 主食类

| 菜品名 | 搜索关键词 | 预期图片内容 |
|--------|-----------|-------------|
| 宫保鸡丁盖饭 | rice bowl | 🍚 盖浇饭 |
| 炸酱面 | noodles | 🍜 面条 |
| 扬州炒饭 | fried rice | 🍛 炒饭 |
| 饺子 | dumplings | 🥟 饺子 |
| 小笼包 | buns | 🥟 包子 |

### 示例3: 西餐类

| 菜品名 | 搜索关键词 | 预期图片内容 |
|--------|-----------|-------------|
| 牛排 | steak | 🥩 牛排 |
| 意大利面 | pasta | 🍝 意面 |
| 披萨 | pizza | 🍕 披萨 |
| 汉堡 | burger | 🍔 汉堡 |
| 沙拉 | salad | 🥗 沙拉 |

## 🔧 使用方法

### 基础使用

```bash
# 1. 生成数据
python generate_canteen_data.py -n 50

# 2. 下载匹配图片
python generate_canteen_data.py --download-images
```

### 查看匹配结果

```bash
开始下载菜品图片（智能匹配）...
找到 50 道菜品需要下载图片
注意: 使用Unsplash图片源，会根据菜品名称智能匹配相关图片

  ✓ 可乐 -> 搜索关键词: cola
  ✓ 牛排 -> 搜索关键词: steak
  ✓ 宫保鸡丁 -> 搜索关键词: kung pao chicken
  ✓ 珍珠奶茶 -> 搜索关键词: milk tea
  ✓ 炸酱面 -> 搜索关键词: noodles
  进度: 10/50 (20.0%)
  ...

完成！成功: 48, 失败: 2

匹配示例:
  可乐 -> cola
  牛排 -> steak
  宫保鸡丁 -> kung pao chicken
```

## 📝 扩展关键词库

### 添加新的菜品映射

编辑 `generate_canteen_data.py` 第267行的 `food_keywords` 字典：

```python
food_keywords = {
    # 已有映射
    '可乐': 'cola',
    '牛排': 'steak',
    
    # 添加你的新映射
    '糖醋排骨': 'sweet and sour pork',
    '小龙虾': 'crayfish',
    '北京烤鸭': 'peking duck',
    '火锅': 'hot pot',
    '煎饼果子': 'chinese crepe',
    '油条': 'fried dough stick',
    '豆浆': 'soy milk',
    
    # 更多...
}
```

### 添加类别关键词

编辑第295行的 `category_keywords` 字典：

```python
category_keywords = {
    '主食': 'asian food',
    '川菜': 'sichuan food',
    '粤菜': 'cantonese food',
    
    # 添加你的新类别
    '东北菜': 'northeastern chinese food',
    '新疆菜': 'xinjiang food',
}
```

## 🌟 技术细节

### 图片来源

使用 **Unsplash Source API**：
- ✅ 免费，无需API key
- ✅ 高质量食物图片
- ✅ 支持关键词搜索
- ✅ 每次请求返回相关但不同的图片

**API格式：**
```
https://source.unsplash.com/800x600/?food,{关键词}
```

**示例：**
```
https://source.unsplash.com/800x600/?food,cola        # 可乐图片
https://source.unsplash.com/800x600/?food,steak       # 牛排图片
https://source.unsplash.com/800x600/?food,pizza       # 披萨图片
```

### 匹配算法

```python
def get_food_image_url(dish_name, category):
    # 1. 尝试直接匹配菜品名中的关键词
    for keyword, english in food_keywords.items():
        if keyword in dish_name:
            search_term = english
            break
    
    # 2. 如果没匹配到，使用类别关键词
    if not found:
        search_term = category_keywords.get(category, 'chinese food')
    
    # 3. 构建Unsplash URL
    url = f"https://source.unsplash.com/800x600/?food,{search_term}"
    
    return url, search_term
```

### 文件命名

下载的图片文件名包含菜品ID和名称：
```
dish_1_可乐.jpg
dish_2_牛排.jpg
dish_3_宫保鸡丁.jpg
```

## ⚠️ 注意事项

### 1. 图片相关性

- **高相关**：西餐、饮品、常见菜品（匹配度>80%）
- **中等相关**：中式特色菜（匹配度50-80%）
- **低相关**：生僻菜品（匹配度<50%，会使用类别关键词）

### 2. 图片多样性

由于Unsplash会返回不同的图片，即使同样的关键词，每次下载的图片也可能不同。

### 3. 网络要求

- 需要稳定的网络连接
- 下载500张图片约需5-10分钟
- 建议在空闲时段运行

### 4. 匹配限制

部分中式传统菜品可能在Unsplash上图片较少，这些菜品会：
1. 尝试使用菜品名中的通用词（如"鱼"、"肉"）
2. 回退到类别关键词（如"川菜"→"sichuan food"）
3. 最终回退到"chinese food"

## 🔄 替代方案

### 方案1: 使用本地图片库

如果对图片质量要求很高：

```python
# 1. 准备图片文件夹
media/dish_images/
├── 可乐.jpg
├── 牛排.jpg
├── 宫保鸡丁.jpg
└── ...

# 2. 修改脚本使用本地图片
# （需要自己实现图片匹配和上传逻辑）
```

### 方案2: 使用其他图片API

可以替换为其他图片源：
- **Pexels API**: 免费，需要API key
- **Pixabay API**: 免费，需要API key
- **自建图片库**: 完全控制

### 方案3: 手动上传

对于重要菜品，可以手动上传精选图片：
1. 使用Django Admin后台
2. 或使用API批量上传

## 📈 效果对比

| 方案 | 相关性 | 质量 | 成本 | 难度 |
|------|--------|------|------|------|
| 智能匹配（当前） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 | 简单 |
| 随机占位图 | ⭐ | ⭐⭐⭐ | 免费 | 最简单 |
| 本地图片库 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 高 | 复杂 |
| 手动上传 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中 | 中等 |

## 🎉 总结

**智能匹配系统** 能够：
- ✅ 自动识别菜品名称
- ✅ 匹配相关图片
- ✅ 免费且高质量
- ✅ 易于扩展

**最适合：** 快速部署、开发测试、原型展示

**建议：** 
- 开发阶段使用智能匹配
- 生产环境可混合使用（重要菜品手动上传，其他菜品智能匹配）

---

**使用愉快！** 如有问题，请查看 README.md 或提交Issue。
