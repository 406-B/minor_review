# 评分系统更新说明

## 更新内容

### 1. 数据库模型更新 (list/models.py)

在 `Dish` 模型中添加了新字段：

```python
rating_count = models.IntegerField(
    default=0, help_text="Number of ratings this dish has received"
)
```

**字段说明**：
- `rating_count`: 评分人数，记录有多少用户给该菜品评过分
- 默认值为 0
- 每次新用户评分时 +1，用户修改评分时保持不变

### 2. 评分逻辑更新 (list/views.py)

修改了 `rate_dish` 函数的评分计算逻辑：

#### 新用户评分
```python
新评分人数 = 旧评分人数 + 1
新评分 = (旧评分 × 旧评分人数 + 新评分) / 新评分人数
```

#### 用户修改评分
```python
新评分人数 = 旧评分人数  # 人数不变
新评分 = (旧评分 × 旧评分人数 - 旧用户评分 + 新用户评分) / 旧评分人数
```

### 3. 初始化脚本

#### init_rating_count.py
用于初始化现有菜品的评分人数：
- 将所有菜品的 `rating_count` 随机设置在 0-200 之间
- 提供统计信息和分布情况

**使用方法**：
```bash
cd src/backend/app
python data_filing/init_rating_count.py
```

#### test_rating_logic.py
测试评分计算逻辑的正确性：
- 验证各种场景下的评分计算
- 确保增量计算与批量计算结果一致

**使用方法**：
```bash
cd src/backend/app
python data_filing/test_rating_logic.py
```

## 数据库迁移

需要创建并应用数据库迁移：

```bash
cd src/backend/app
python manage.py makemigrations list
python manage.py migrate
```

## API 响应变化

评分接口 `/api/dishes/{dish_id}/rate/` 的响应增加了 `rating_count` 字段：

```json
{
    "code": 200,
    "message": "评分成功",
    "data": {
        "dish_id": 1,
        "user_score": 4.5,
        "new_rating": 4.2,
        "rating_count": 101
    }
}
```

## 优势

### 1. 性能优化
- **旧方案**: 每次评分都需要查询所有评分记录并计算平均值 `O(n)`
- **新方案**: 使用增量更新，只需简单的算术运算 `O(1)`

### 2. 数据完整性
- 评分人数独立记录，不依赖于评分记录表的查询
- 即使评分记录被删除，评分人数仍然准确

### 3. 用户体验
- 显示评分人数，让用户了解评分的可信度
- 评分人数多的菜品更有参考价值

## 注意事项

1. **数据迁移**：现有数据库需要运行迁移脚本
2. **初始化**：使用 `init_rating_count.py` 初始化现有菜品的评分人数
3. **兼容性**：旧的评分数据会自动适配新逻辑
4. **精度**：评分结果保留两位小数

## 测试建议

1. 运行测试脚本验证计算逻辑
2. 测试新用户评分场景
3. 测试用户修改评分场景
4. 验证评分人数统计正确性
5. 检查 API 响应格式

## 示例场景

### 场景1：菜品初始状态
```
rating = 0.0, rating_count = 0
用户A评分 4.5
→ rating = 4.5, rating_count = 1
```

### 场景2：已有评分
```
rating = 4.5, rating_count = 1
用户B评分 3.5
→ rating = (4.5×1 + 3.5) / 2 = 4.0, rating_count = 2
```

### 场景3：修改评分
```
rating = 4.0, rating_count = 2
用户B将评分从3.5改为5.0
→ rating = (4.0×2 - 3.5 + 5.0) / 2 = 4.75, rating_count = 2
```

## 数学验证

增量计算公式的正确性：

设已有 n 个评分，平均分为 r̄，总分 S = r̄ × n

新增评分 x 后：
- 新总分：S' = S + x = r̄ × n + x
- 新人数：n' = n + 1
- 新平均：r̄' = S' / n' = (r̄ × n + x) / (n + 1)

修改评分从 x_old 到 x_new：
- 新总分：S' = S - x_old + x_new = r̄ × n - x_old + x_new
- 新人数：n' = n（不变）
- 新平均：r̄' = S' / n = (r̄ × n - x_old + x_new) / n

✓ 公式数学正确
