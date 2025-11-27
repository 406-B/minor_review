# 用户偏好标签功能实现总结

## 概述

已完成用户偏好标签功能的后端实现，允许新用户注册后选择菜品标签作为个性化推荐依据，并在个人资料界面查看推荐菜品和管理偏好标签。

## 实现的功能

### 1. 数据库模型修改

**文件：** `src/backend/app/login/models.py`

在 `User` 模型中新增了 `preference_tags` 字段（多对多关系），用于存储用户的偏好标签。

**迁移文件：** `src/backend/app/login/migrations/0004_user_preference_tags.py`

### 2. 序列化器

**文件：** `src/backend/app/profile/serializers.py`

- 修改了 `UserProfileSerializer`，添加了 `preference_tags` 字段的序列化
- 新增了 `UserPreferenceTagsSerializer`，用于验证和处理偏好标签的设置

### 3. API 接口

**文件：** `src/backend/app/profile/views.py`

新增了以下 4 个 API 视图：

#### (1) 获取用户偏好标签

- **接口：** `GET /api/profile/preference-tags`
- **功能：** 获取当前登录用户的所有偏好标签
- **权限：** 需要登录

#### (2) 设置用户偏好标签（覆盖模式）

- **接口：** `POST /api/profile/preference-tags/set` 或 `PUT /api/profile/preference-tags/set`
- **功能：** 设置用户偏好标签，覆盖原有标签
- **权限：** 需要登录
- **用途：** 新用户注册后首次选择偏好标签

#### (3) 添加偏好标签（追加模式）

- **接口：** `POST /api/profile/preference-tags/add`
- **功能：** 向用户偏好标签列表中添加新标签，不覆盖原有标签
- **权限：** 需要登录
- **用途：** 用户在个人资料界面添加新的偏好标签

#### (4) 获取个性化推荐菜品

- **接口：** `GET /api/profile/recommended-dishes`
- **功能：** 根据用户偏好标签推荐菜品
- **推荐算法：**
  - 匹配用户偏好标签的菜品
  - 按匹配标签数量、评分、浏览量排序
  - 支持分页
- **权限：** 需要登录

### 4. URL 路由配置

**文件：** `src/backend/app/profile/urls.py`

新增了以下路由：

```python
path("profile/preference-tags", views.get_preference_tags, name="get_preference_tags"),
path("profile/preference-tags/set", views.set_preference_tags, name="set_preference_tags"),
path("profile/preference-tags/add", views.add_preference_tags, name="add_preference_tags"),
path("profile/recommended-dishes", views.get_recommended_dishes, name="get_recommended_dishes"),
```

## 使用流程

### 流程 1：新用户注册后设置偏好标签

1. 用户完成注册
2. 前端展示标签选择页面
3. 调用 `GET /api/list/tags/` 获取所有可用标签
4. 用户选择多个标签
5. 调用 `POST /api/profile/preference-tags/set` 提交偏好标签

### 流程 2：个人资料界面查看推荐菜品

1. 用户进入个人资料界面
2. 调用 `GET /api/profile/preference-tags` 获取用户偏好标签（显示在界面上）
3. 调用 `GET /api/profile/recommended-dishes` 获取推荐菜品列表
4. 展示推荐菜品

### 流程 3：在个人资料界面添加偏好标签

1. 用户在个人资料界面点击"添加偏好标签"
2. 调用 `GET /api/list/tags/` 获取所有可用标签
3. 用户选择要添加的标签
4. 调用 `POST /api/profile/preference-tags/add` 添加标签
5. 刷新推荐菜品列表

## 技术要点

### 1. 推荐算法

使用 Django ORM 的 `annotate` 和 `Count` 实现智能推荐：

```python
dishes = Dish.objects.filter(
    tags__in=user_tags
).annotate(
    matched_tags_count=Count('tags', filter=Q(tags__in=user_tags))
).distinct().order_by('-matched_tags_count', '-rating', '-view_count')
```

**排序逻辑：**

1. 优先推荐匹配标签数量多的菜品
2. 其次按菜品评分排序
3. 最后按浏览量排序

### 2. 覆盖 vs 追加模式

- **覆盖模式（set）：** 使用 `user.preference_tags.set(tags)`，适合新用户首次设置
- **追加模式（add）：** 使用 `user.preference_tags.add(*tags)`，适合用户后续添加标签

### 3. OpenAPI 文档集成

所有接口都使用 `drf_spectacular` 的 `@extend_schema` 装饰器，自动生成 OpenAPI 文档。

## 数据库迁移

**执行迁移：**

```bash
cd src/backend/app
python manage.py migrate login
```

**迁移内容：**

- 创建 `login_user_preference_tags` 中间表
- 建立 User 和 Tag 的多对多关系

## 文档

详细的 API 文档请参考：
`src/backend/app/profile/PREFERENCE_TAGS_API.md`

## 测试建议

### 1. 单元测试

- 测试用户偏好标签的设置和获取
- 测试推荐算法的正确性
- 测试边界情况（无偏好标签、标签不存在等）

### 2. 接口测试

- 使用 Postman 或类似工具测试所有新接口
- 测试不同用户的偏好标签相互独立
- 测试分页功能

### 3. 集成测试

- 测试完整的用户注册-选择偏好-查看推荐流程
- 测试在个人资料界面添加标签后推荐更新

## 后续优化建议

1. **推荐算法优化：**
   - 考虑用户的历史浏览和评分记录
   - 引入协同过滤算法
   - 添加时间衰减因子（优先推荐新菜品）

2. **缓存机制：**
   - 对推荐结果进行缓存
   - 减少数据库查询

3. **个性化程度：**
   - 记录用户对推荐菜品的反馈
   - 动态调整推荐权重

4. **标签管理：**
   - 允许用户移除已选择的偏好标签
   - 添加标签使用热度统计

## 注意事项

1. 所有接口都需要用户登录（使用 `@login_required` 装饰器）
2. 使用覆盖模式时会删除用户原有的所有偏好标签
3. 推荐接口要求用户至少设置一个偏好标签，否则返回 404
4. tag_ids 参数必须是数组格式

## 完成状态

✅ 数据库模型修改  
✅ 创建数据库迁移文件  
✅ 添加序列化器  
✅ 创建 API 视图（获取/设置偏好标签）  
✅ 创建 API 视图（推荐菜品）  
✅ 配置 URL 路由  
✅ 编写 API 文档

**所有任务已完成！** 🎉
