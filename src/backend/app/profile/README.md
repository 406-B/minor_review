# Profile 应用

## 概述

profile应用负责处理用户个人资料相关的所有功能，包括个人资料的查看、更新、密码修改和统计信息获取。

## 功能模块

### 1. 个人资料管理
- 获取个人资料信息
- 更新昵称
- 更新头像（支持图片上传）

### 2. 密码管理
- 修改密码（需验证旧密码）
- 密码强度验证

### 3. 用户统计 🆕
- 点赞的帖子数量
- 评论的帖子数量
- 关注的人数量

## 文件结构

```
profile/
├── __init__.py
├── apps.py              # 应用配置
├── admin.py             # 管理后台配置（预留）
├── models.py            # 模型定义（当前不定义新模型）
├── serializers.py       # 数据序列化器
├── controllers.py       # 业务逻辑控制器
├── views.py             # 视图函数
├── urls.py              # 路由配置
├── tests.py             # 单元测试（待完善）
└── migrations/          # 数据库迁移文件
    └── __init__.py
```

## API端点

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/api/v1/profile` | 获取个人资料 | ✅ |
| PUT/PATCH | `/api/v1/profile/update` | 更新个人资料 | ✅ |
| POST | `/api/v1/profile/password` | 修改密码 | ✅ |
| GET | `/api/v1/profile/stats` | 获取统计信息 | ✅ |

## 依赖关系

### 依赖的应用
- `login`: 使用User模型
- `utils`: 使用JWT认证工具

### 被依赖的应用
- 无（独立应用）

## 数据模型

profile应用本身不定义新的数据模型，直接使用 `login.models.User` 模型。

User模型包含以下字段：
- `id`: 主键
- `username`: 用户名（唯一）
- `password`: 加密密码
- `nickname`: 昵称
- `avatar`: 头像（ImageField）
- `created`: 创建时间
- `updated`: 更新时间

## 业务逻辑

### 1. 更新个人资料 (controllers.py)

```python
update_user_profile(user, nickname=None, avatar=None)
```

- 支持单独更新昵称或头像
- 支持同时更新两者
- 至少需要提供一个更新字段

### 2. 更新密码 (controllers.py)

```python
update_user_password(user, new_password)
```

- 接收加密后的新密码
- 更新用户密码字段

### 3. 获取统计信息 (controllers.py)

```python
get_user_stats(user)
```

- 返回用户统计信息字典
- 当前返回默认值0
- TODO: 实现实际的数据库查询逻辑

## 序列化器

### UserProfileSerializer
完整的用户资料序列化器，包含所有公开字段。

### UpdateProfileSerializer
用于更新资料的序列化器，支持部分字段更新。

### UpdatePasswordSerializer
密码修改序列化器，包含验证逻辑：
- 验证两次新密码是否一致
- 验证密码长度（最少6位）

### UserStatsSerializer
统计信息序列化器，包含：
- liked_posts_count: 点赞数
- commented_posts_count: 评论数
- following_count: 关注数

## 安全性

### 认证
- 所有端点都需要JWT Token认证
- 使用 `@login_required` 装饰器

### 验证
- 昵称不能为空
- 密码长度至少6位
- 修改密码需验证旧密码
- 两次新密码必须一致

### 数据保护
- 用户只能访问和修改自己的资料
- 密码使用scrypt加密存储
- 头像上传时验证文件类型

## 测试

### 单元测试（待完善）

创建测试文件 `tests.py`，测试用例应包括：

1. **获取个人资料测试**
   - 测试已登录用户获取资料
   - 测试未登录用户被拒绝

2. **更新资料测试**
   - 测试更新昵称
   - 测试更新头像
   - 测试同时更新
   - 测试无效输入

3. **修改密码测试**
   - 测试正常修改
   - 测试旧密码错误
   - 测试新密码不一致
   - 测试密码长度不足

4. **统计信息测试**
   - 测试获取统计信息
   - 测试返回值格式

### 手动测试

使用提供的测试脚本：
```bash
bash test_profile_api.sh
```

或使用Apifox导入 `docs/api/openapi.json` 进行测试。

## 待实现功能

### 高优先级
1. ✅ 基础个人资料管理
2. ✅ 密码修改
3. ✅ 统计信息API接口
4. ⏳ 实现实际的统计逻辑

### 中优先级
1. ⏳ 完善单元测试
2. ⏳ 头像压缩优化
3. ⏳ 支持更多个人资料字段

### 低优先级
1. ⏳ 头像裁剪功能
2. ⏳ 资料修改历史记录
3. ⏳ 头像审核机制

## 注意事项

1. **图片上传**
   - 建议前端限制图片大小（5MB以内）
   - 支持格式：JPG, PNG, GIF
   - 图片保存在 `media/avatars/` 目录

2. **性能考虑**
   - 统计信息未来需要缓存优化
   - 大量用户时考虑异步处理头像

3. **扩展性**
   - controllers.py 中的函数便于单元测试
   - serializers.py 便于API版本控制
   - 独立应用便于微服务化

## 更新日志

- **2025-11-02**: 
  - 创建profile应用
  - 实现基础个人资料功能
  - 添加统计信息API
  - 从login应用迁移相关功能
