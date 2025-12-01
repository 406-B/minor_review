# 🎯 食堂数据自动生成工具 - 文档导航

欢迎使用食堂数据自动生成工具！本工具可以为餐厅自动创建完整的数据结构。

## 📂 文件结构

```
data_filing/
├── generate_canteen_data.py    # 主程序（全功能集成）
├── run.bat                      # Windows快捷启动脚本
├── INDEX.md                     # 本文档（导航索引）
├── README.md                    # 完整使用文档
├── EXAMPLES.md                  # 使用示例集合
└── IMAGE_MATCHING.md            # 图片智能匹配系统说明 ⭐
```

## 🚀 新手入门 - 30秒快速开始

**方式1: 使用批处理文件（Windows，最简单）**
```bash
双击 run.bat
选择选项 1（快速生成）
```

**方式2: 命令行**
```bash
cd src/backend/app/data_filing
python generate_canteen_data.py
```

完成！数据已生成。

## 📚 文档说明

### 1️⃣ [README.md](README.md) - 完整文档
**适合**: 需要深入了解的用户  
**内容**:
- 功能特性详解
- 所有参数说明
- 生成数据详情
- 高级配置方法
- 图片处理方案
- 常见问题解答

**阅读时间**: 15分钟

---

### 2️⃣ [EXAMPLES.md](EXAMPLES.md) - 使用示例
**适合**: 想看具体例子的用户  
**内容**:
- 12个真实使用场景
- 每个场景的完整命令
- 预期输出示例
- 快速命令参考卡

**阅读时间**: 10分钟

---

### 3️⃣ [IMAGE_MATCHING.md](IMAGE_MATCHING.md) - 图片智能匹配 ⭐
**适合**: 关心图片质量的用户  
**内容**:
- 🎯 图片匹配原理
- 📊 60+关键词映射表
- 🔧 如何扩展关键词库
- 💡 匹配效果展示
- ⚙️ 技术实现细节

**阅读时间**: 8分钟

**重点解决**:
- ✅ 如何让可乐显示可乐的图片？
- ✅ 如何让牛排显示牛排的图片？
- ✅ 如何自定义菜品图片映射？

---

## 🎓 学习路径

### 完全新手
```
1. 阅读 README.md 的"快速开始"部分（3分钟）
2. 运行 run.bat 或执行快速生成命令
3. 查看 EXAMPLES.md 的示例1-3
```

### 关心图片匹配
```
1. 直接阅读 IMAGE_MATCHING.md（8分钟）
2. 运行图片下载命令查看效果
3. 根据需要扩展关键词库
```

### 有经验用户
```
1. 浏览 README.md 的参数说明部分
2. 查看 EXAMPLES.md 选择合适的场景
3. 根据需要查阅 README.md 的高级配置
```

## ⚡ 常用命令速查

```bash
# 查看帮助
python generate_canteen_data.py --help

# 快速生成（40-60道菜/餐厅）
python generate_canteen_data.py

# 指定数量生成
python generate_canteen_data.py -n 100

# 查看统计
python generate_canteen_data.py --stats

# 清空数据
python generate_canteen_data.py --clear-only

# 清空并重新生成
python generate_canteen_data.py --clear

# 下载图片（智能匹配）⭐
python generate_canteen_data.py --download-images

# 自定义价格范围
python generate_canteen_data.py --min-price 10 --max-price 30
```

## 🖼️ 图片智能匹配特性 ⭐

**新功能！** 根据菜品名称自动匹配相关图片：

| 菜品 | 搜索关键词 | 匹配图片 |
|------|-----------|---------|
| 可乐 | cola | 🥤 可乐图片 |
| 牛排 | steak | 🥩 牛排图片 |
| 宫保鸡丁 | kung pao chicken | 🍗 宫保鸡丁图片 |
| 珍珠奶茶 | milk tea | 🧋 奶茶图片 |
| 披萨 | pizza | 🍕 披萨图片 |

**详细说明**: 查看 [IMAGE_MATCHING.md](IMAGE_MATCHING.md)

## 🔍 快速查找

**我想...**
- **了解图片如何匹配** → IMAGE_MATCHING.md ⭐
- **第一次使用** → README.md 的"快速开始"部分
- **了解所有功能** → README.md 的"功能特性"部分
- **查看命令参数** → README.md 的"参数说明"部分
- **看具体例子** → EXAMPLES.md
- **解决问题** → README.md 的"常见问题"部分
- **修改配置** → README.md 的"高级配置"部分
- **扩展关键词库** → IMAGE_MATCHING.md 的"扩展关键词库"部分

## 📊 核心功能概览

| 功能 | 说明 | 命令示例 |
|------|------|----------|
| 快速生成 | 每餐厅40-60道菜 | `python generate_canteen_data.py` |
| 自定义数量 | 指定每餐厅菜品数 | `python generate_canteen_data.py -n 100` |
| 数据统计 | 查看当前数据概况 | `python generate_canteen_data.py --stats` |
| 清空数据 | 删除所有生成的数据 | `python generate_canteen_data.py --clear-only` |
| 重置数据 | 清空并重新生成 | `python generate_canteen_data.py --clear` |
| 智能下载图片 ⭐ | 根据菜品名匹配图片 | `python generate_canteen_data.py --download-images` |
| 价格控制 | 自定义价格范围 | `python generate_canteen_data.py --min-price 10 --max-price 30` |

## 🎯 生成内容一览

✅ **楼层**: 每个餐厅1-3层  
✅ **窗口**: 每层3-8个窗口  
✅ **菜品**: 9大类别，200+道菜  
✅ **标签**: 60+个智能标签  
✅ **价格**: ¥2-45（根据类别）  
✅ **评分**: 3.5-5.0分  
✅ **描述**: 智能生成的详细描述  
✅ **图片**: 智能匹配下载（可乐→可乐图片）⭐  

## ⚠️ 重要提示

1. **运行环境**: 必须在Django环境中运行
2. **数据库**: 需要先有餐厅（Canteen）数据
3. **清空操作**: `--clear` 会删除所有数据，不可恢复！
4. **图片下载**: 需要先安装 `pip install requests`

## 🆘 需要帮助？

1. **查看帮助信息**: `python generate_canteen_data.py --help`
2. **查看统计**: `python generate_canteen_data.py --stats`
3. **阅读常见问题**: README.md 的"常见问题"部分
4. **查看示例**: EXAMPLES.md
5. **了解图片匹配**: IMAGE_MATCHING.md

## 📞 技术支持

遇到问题时的排查步骤：
1. 检查是否在正确的目录（`src/backend/app/data_filing`）
2. 检查Django环境是否正确
3. 查看 `--stats` 输出的当前数据状态
4. 查阅相应文档的"常见问题"部分
5. 查看Python错误信息

---

**推荐阅读顺序**:  
📖 README.md → 📋 EXAMPLES.md → 🖼️ IMAGE_MATCHING.md

**祝使用愉快！** 🎉
