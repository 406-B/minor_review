# 使用示例

本文档提供各种使用场景的具体示例。

## 示例 1: 首次部署

**场景**: 第一次部署系统，需要生成初始数据

```bash
# 步骤1: 检查是否有餐厅数据
cd src/backend/app/data_filing
python generate_canteen_data.py --stats

# 输出示例:
# 📊 基础数据:
#   ✓ 餐厅数量: 10
#   ✓ 菜品总数: 0      # 还没有菜品
#   ✓ 标签总数: 0
#   ✓ 楼层总数: 0
#   ✓ 窗口总数: 0

# 步骤2: 生成数据（每餐厅50道菜）
python generate_canteen_data.py -n 50

# 步骤3: 验证生成结果
python generate_canteen_data.py --stats

# 输出示例:
# 📊 基础数据:
#   ✓ 餐厅数量: 10
#   ✓ 菜品总数: 500
#   ✓ 标签总数: 65
#   ✓ 楼层总数: 18
#   ✓ 窗口总数: 95
#   ✓ 平均每餐厅: 50.0 道菜
#   ✓ 平均每餐厅: 1.8 层楼
#   ✓ 平均每餐厅: 9.5 个窗口

# 步骤4（可选）: 下载图片
pip install requests
python generate_canteen_data.py --download-images
```

## 示例 2: 开发测试

**场景**: 开发时需要测试功能，需要少量数据

```bash
# 生成少量测试数据
python generate_canteen_data.py -n 10

# 测试功能...

# 测试完成，清空数据
python generate_canteen_data.py --clear-only

# 重新生成新的测试数据
python generate_canteen_data.py -n 15
```

## 示例 3: 数据重置

**场景**: 测试数据混乱，需要完全重置

```bash
# 方式1: 使用 --clear 参数（一步完成）
python generate_canteen_data.py --clear -n 50

# 方式2: 分步操作
python generate_canteen_data.py --clear-only  # 先清空
python generate_canteen_data.py -n 50         # 再生成
```

## 示例 4: 自定义价格范围

**场景**: 需要设置统一的价格区间

```bash
# 所有菜品价格在10-25元之间
python generate_canteen_data.py -n 60 --min-price 10 --max-price 25

# 低价位餐厅（5-15元）
python generate_canteen_data.py -n 50 --min-price 5 --max-price 15

# 高端餐厅（20-50元）
python generate_canteen_data.py --clear -n 40 --min-price 20 --max-price 50
```

## 示例 5: 补充数据

**场景**: 已有数据，想添加更多菜品

```bash
# 查看当前数据
python generate_canteen_data.py --stats
# 输出: 平均每餐厅: 30.0 道菜

# 不使用 --clear，直接添加（如果菜品名不重复会新增）
python generate_canteen_data.py -n 20

# 再次查看
python generate_canteen_data.py --stats
# 输出: 平均每餐厅: 50.0 道菜（约）
```

## 示例 6: 批量操作

**场景**: 多次生成不同配置的数据进行对比测试

```bash
# 方案A: 默认价格，50道菜
python generate_canteen_data.py --clear -n 50
python generate_canteen_data.py --stats > stats_plan_a.txt

# 方案B: 统一价格，100道菜
python generate_canteen_data.py --clear -n 100 --min-price 8 --max-price 20
python generate_canteen_data.py --stats > stats_plan_b.txt

# 对比两个方案的统计数据
# 可以查看 stats_plan_a.txt 和 stats_plan_b.txt
```

## 示例 7: 仅下载图片

**场景**: 数据已生成，只需要补充图片

```bash
# 确保已安装requests
pip install requests

# 只下载图片，不生成数据
python generate_canteen_data.py --download-images

# 输出示例:
# 找到 500 道菜品需要下载图片
#   进度: 10/500 (2.0%)
#   进度: 20/500 (4.0%)
#   ...
# 完成！成功: 495, 失败: 5
```

## 示例 8: 使用批处理文件（Windows）

**场景**: 不想记命令，使用图形化菜单

```bash
# 双击 run.bat 或命令行运行
run.bat

# 会看到菜单:
# ============================================================
#            食堂数据自动生成工具
# ============================================================
# 
# 请选择操作:
# 
#   1. 快速生成数据（每餐厅40-60道菜）
#   2. 生成大量数据（每餐厅100道菜）
#   3. 生成少量数据（每餐厅20道菜）
#   4. 查看数据统计
#   5. 清空所有数据（不生成新数据）
#   6. 清空并重新生成数据
#   7. 下载菜品图片
#   8. 查看帮助信息
#   0. 退出
# 
# ============================================================
# 请输入选项 (0-8): 1

# 输入选项号，按回车即可
```

## 示例 9: 在Python代码中使用

**场景**: 需要在其他Python脚本或Django管理命令中调用

```python
# 在Django项目的其他Python文件中

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_filing'))

from generate_canteen_data import (
    generate_dishes,
    clear_data,
    show_statistics,
    download_images
)

# 清空数据
clear_data()

# 生成数据
generate_dishes(
    num_dishes_per_canteen=80,
    min_price=10.0,
    max_price=30.0
)

# 显示统计
show_statistics()

# 下载图片
download_images()
```

## 示例 10: 组合参数使用

**场景**: 一次性完成所有操作

```bash
# 清空数据，生成60道菜，价格10-28元
python generate_canteen_data.py --clear -n 60 --min-price 10 --max-price 28

# 然后下载图片
python generate_canteen_data.py --download-images

# 最后查看统计
python generate_canteen_data.py --stats
```

## 示例 11: 定期维护

**场景**: 每周添加新菜品保持数据新鲜

```bash
# 周一: 查看当前数据
python generate_canteen_data.py --stats

# 周三: 添加一些新菜品（不清空原有数据）
python generate_canteen_data.py -n 10

# 周五: 再次查看统计
python generate_canteen_data.py --stats
```

## 示例 12: 错误排查

**场景**: 遇到问题需要排查

```bash
# 1. 先查看帮助
python generate_canteen_data.py --help

# 2. 检查当前数据状态
python generate_canteen_data.py --stats

# 3. 如果数据异常，清空重新生成
python generate_canteen_data.py --clear -n 50

# 4. 如果还有问题，查看Python错误信息
python generate_canteen_data.py 2> error.log

# 5. 检查 error.log 文件查看详细错误
```

## 快速命令参考卡

```bash
# 最常用的5个命令
python generate_canteen_data.py              # 快速生成
python generate_canteen_data.py --stats      # 查看统计
python generate_canteen_data.py --clear      # 重置数据
python generate_canteen_data.py -n 100       # 生成100道菜
python generate_canteen_data.py --help       # 查看帮助

# 高级用法
python generate_canteen_data.py --clear -n 80 --min-price 8 --max-price 25
python generate_canteen_data.py --clear-only
python generate_canteen_data.py --download-images
```

---

## 💡 小贴士

1. **首次使用**: 先运行 `--stats` 查看当前状态
2. **测试环境**: 使用 `-n 20` 生成少量数据即可
3. **生产环境**: 建议使用 `-n 80` 或更多
4. **数据重置**: 务必确认后再使用 `--clear`
5. **图片下载**: 耗时较长，建议在空闲时段运行
6. **参数组合**: 可以同时使用多个参数，如 `--clear -n 100 --min-price 10`

如有其他问题，请查看 `README.md` 获取完整文档。
