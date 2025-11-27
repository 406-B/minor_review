# 用户偏好标签功能 API 文档

## 功能概述

本功能为用户提供个性化推荐系统，用户可以选择喜欢的菜品标签作为偏好，系统会根据这些偏好标签推荐相应的菜品。

## 数据库变更

### User 模型新增字段

在 `login.models.User` 模型中新增：

```python
preference_tags = models.ManyToManyField(
    'list.Tag',
    blank=True,
    related_name='preferred_by_users',
    verbose_name="偏好标签"
)
```

### 数据库迁移

已创建迁移文件：`login/migrations/0004_user_preference_tags.py`

运行迁移命令：

```bash
cd src/backend/app
python manage.py migrate login
```

## API 接口

### 1. 获取用户偏好标签

**接口地址：** `GET /api/profile/preference-tags`

**请求头：**

- `Authorization: Bearer <token>` (必需)

**响应示例：**

```json
{
  "code": 200,
  "message": "获取偏好标签成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 25,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "素食",
      "dish_count": 18,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 2. 设置用户偏好标签（覆盖模式）

**接口地址：** `POST /api/profile/preference-tags/set` 或 `PUT /api/profile/preference-tags/set`

**请求头：**

- `Authorization: Bearer <token>` (必需)
- `Content-Type: application/json`

**请求体：**

```json
{
  "tag_ids": [1, 2, 3, 5]
}
```

**说明：**

- 此接口会覆盖用户原有的所有偏好标签
- 适用于新用户注册后首次选择偏好标签的场景

**响应示例：**

```json
{
  "code": 200,
  "message": "偏好标签设置成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 25,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "素食",
      "dish_count": 18,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 3. 添加偏好标签（追加模式）

**接口地址：** `POST /api/profile/preference-tags/add`

**请求头：**

- `Authorization: Bearer <token>` (必需)
- `Content-Type: application/json`

**请求体：**

```json
{
  "tag_ids": [6, 7]
}
```

**说明：**

- 此接口会在用户现有偏好标签的基础上追加新标签
- 适用于用户在个人资料界面添加新偏好标签的场景

**响应示例：**

```json
{
  "code": 200,
  "message": "偏好标签添加成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 25
    },
    {
      "id": 2,
      "name": "素食",
      "dish_count": 18
    },
    {
      "id": 6,
      "name": "清淡",
      "dish_count": 20
    },
    {
      "id": 7,
      "name": "海鲜",
      "dish_count": 15
    }
  ]
}
```

### 4. 获取个性化推荐菜品

**接口地址：** `GET /api/profile/recommended-dishes`

**请求头：**

- `Authorization: Bearer <token>` (必需)

**查询参数：**

- `page`: 页码，默认 1
- `page_size`: 每页数量，默认 20
- `limit`: 返回数量（废弃，建议使用 page_size）

**推荐算法：**

1. 获取用户的偏好标签
2. 查询包含这些标签的菜品
3. 按以下优先级排序：
   - 匹配的标签数量（越多越靠前）
   - 菜品评分（越高越靠前）
   - 浏览次数（越多越靠前）

**响应示例：**

```json
{
  "code": 200,
  "message": "获取推荐菜品成功",
  "data": {
    "dishes": [
      {
        "id": 1,
        "name": "麻辣香锅",
        "price": "28.00",
        "image": "/media/dishes/malaxiangguo.jpg",
        "canteen_name": "学一食堂",
        "tags": [
          {
            "id": 1,
            "name": "辣",
            "dish_count": 25
          },
          {
            "id": 3,
            "name": "热门",
            "dish_count": 30
          }
        ],
        "rating": "4.50",
        "view_count": 1250,
        "window": {
          "id": 1,
          "name": "川菜窗口",
          "order": 1
        }
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20,
    "user_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 25
      },
      {
        "id": 2,
        "name": "素食",
        "dish_count": 18
      }
    ]
  }
}
```

**错误响应（未设置偏好标签）：**

```json
{
  "code": 404,
  "message": "用户未设置偏好标签，请先设置偏好标签",
  "data": null
}
```

### 5. 获取所有可用标签

**接口地址：** `GET /api/list/tags`

**说明：** 此接口已存在，用于获取系统中所有可用的标签，供用户选择偏好标签时使用。

**响应示例：**

```json
{
  "code": 200,
  "message": "获取标签列表成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 25,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "素食",
      "dish_count": 18,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## 使用场景

### 场景1：新用户注册后设置偏好标签

1. 用户完成注册
2. 前端调用 `GET /api/list/tags` 获取所有可用标签
3. 用户选择多个偏好标签
4. 前端调用 `POST /api/profile/preference-tags/set` 设置用户偏好

### 场景2：在个人资料界面查看推荐菜品

1. 用户进入个人资料界面
2. 前端调用 `GET /api/profile/preference-tags` 获取用户当前偏好标签
3. 前端调用 `GET /api/profile/recommended-dishes` 获取推荐菜品列表
4. 展示推荐菜品给用户

### 场景3：在个人资料界面添加新的偏好标签

1. 用户在个人资料界面点击"添加偏好标签"
2. 前端调用 `GET /api/list/tags` 获取所有可用标签
3. 用户选择要添加的标签
4. 前端调用 `POST /api/profile/preference-tags/add` 添加新标签
5. 前端刷新推荐菜品列表

## 错误码说明

| 错误码 | 说明                                              |
| ------ | ------------------------------------------------- |
| 200    | 请求成功                                          |
| 400    | 参数错误（如：tag_ids格式不正确、标签ID不存在等） |
| 401    | 未登录或 token 无效                               |
| 404    | 用户未设置偏好标签（仅在获取推荐菜品时）          |

## 注意事项

1. 所有接口都需要用户登录（需要在请求头中携带有效的 token）
2. `set` 接口会覆盖用户原有的所有偏好标签，`add` 接口会在原有基础上追加
3. 推荐菜品接口要求用户至少设置一个偏好标签
4. 推荐算法优先推荐匹配标签数量多的菜品，再按评分和浏览量排序
5. tag_ids 必须是数组格式，即使只有一个标签也要使用数组：`[1]`

## 前端集成示例

### 示例1：新用户注册后选择偏好标签

```javascript
// 1. 获取所有可用标签
const tags = await fetch('/api/list/tags').then((r) => r.json());

// 2. 用户选择标签后提交
const selectedTagIds = [1, 2, 3, 5];
await fetch('/api/profile/preference-tags/set', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({ tag_ids: selectedTagIds }),
});
```

### 示例2：在个人资料界面查看推荐

```javascript
// 1. 获取用户偏好标签
const userTags = await fetch('/api/profile/preference-tags', {
  headers: { Authorization: `Bearer ${token}` },
}).then((r) => r.json());

// 2. 获取推荐菜品
const recommended = await fetch('/api/profile/recommended-dishes?page=1&page_size=20', {
  headers: { Authorization: `Bearer ${token}` },
}).then((r) => r.json());
```

### 示例3：添加新的偏好标签

```javascript
// 用户选择新标签后添加
const newTagIds = [6, 7];
await fetch('/api/profile/preference-tags/add', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({ tag_ids: newTagIds }),
});
```
