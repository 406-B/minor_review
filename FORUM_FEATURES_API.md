# 社区论坛新功能 API 文档

## 📝 新增功能说明

### 1. 评论图片功能
评论和回复现在都支持上传图片，最多可以附加 9 张图片。

### 2. 评论回复功能  
支持对评论进行回复，但仅支持两级结构（只能回复顶级评论）。

### 3. 帖子关联菜品
发布帖子时可以关联特定的菜品，用户可以通过菜品链接查看相关讨论。

---

## 🔗 API 端点

### 1. 创建帖子（支持菜品关联）

**POST** `/api/v1/posts/create/`

**请求参数**：
```json
{
    "subject": "帖子标题",
    "content": "帖子内容", 
    "dish": 123  // 菜品ID，可选
}
```

**响应**：
```json
{
    "code": 200,
    "message": "发布成功",
    "data": {
        "id": 1,
        "author": {
            "id": 1,
            "username": "user1",
            "nickname": "用户1",
            "avatar": "http://example.com/avatar.jpg"
        },
        "subject": "帖子标题",
        "dish": {
            "id": 123,
            "name": "宫保鸡丁",
            "price": "15.00",
            "image": "http://example.com/dish.jpg",
            "canteen_name": "第一食堂"
        },
        "created_at": "2025-11-19T10:00:00Z",
        "likes_count": 0,
        "comments_count": 0,
        "is_liked": false
    }
}
```

### 2. 创建评论（支持图片和回复）

**POST** `/api/v1/comments/create/`

**请求参数**：
```json
{
    "post": 1,  // 帖子ID
    "content": "评论内容",
    "images": [  // 图片URL列表，可选，最多9张
        "http://example.com/image1.jpg",
        "http://example.com/image2.jpg"
    ],
    "parent": 5  // 父评论ID，可选（用于回复）
}
```

**响应**：
```json
{
    "code": 200,
    "message": "评论成功",  // 或 "回复成功"
    "data": {
        "id": 10,
        "post": 1,
        "author": {
            "id": 1,
            "username": "user1",
            "nickname": "用户1",
            "avatar": "http://example.com/avatar.jpg"
        },
        "content": "评论内容",
        "images": [
            "http://example.com/image1.jpg",
            "http://example.com/image2.jpg"
        ],
        "parent": 5,
        "created_at": "2025-11-19T10:05:00Z",
        "likes_count": 0,
        "is_liked": false,
        "replies": []
    }
}
```

### 3. 获取菜品相关帖子

**GET** `/api/v1/dishes/{dish_id}/posts/`

**URL 参数**：
- `dish_id`: 菜品ID

**查询参数**：
- `page`: 页码，默认 1
- `page_size`: 每页数量，默认 20

**响应**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "dish": {
            "id": 123,
            "name": "宫保鸡丁",
            "canteen_name": "第一食堂"
        },
        "posts": [
            {
                "id": 1,
                "author": {
                    "id": 1,
                    "username": "user1",
                    "nickname": "用户1",
                    "avatar": "http://example.com/avatar.jpg"
                },
                "subject": "这道菜真的很好吃",
                "dish": {
                    "id": 123,
                    "name": "宫保鸡丁",
                    "price": "15.00",
                    "image": "http://example.com/dish.jpg",
                    "canteen_name": "第一食堂"
                },
                "created_at": "2025-11-19T10:00:00Z",
                "likes_count": 5,
                "comments_count": 3,
                "is_liked": false
            }
        ],
        "pagination": {
            "total": 15,
            "page": 1,
            "page_size": 20,
            "total_pages": 1
        }
    }
}
```

### 4. 获取帖子详情（包含评论树结构）

**GET** `/api/v1/posts/{post_id}/`

**响应**：
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "author": {
            "id": 1,
            "username": "user1",
            "nickname": "用户1",
            "avatar": "http://example.com/avatar.jpg"
        },
        "subject": "帖子标题",
        "content": "帖子详细内容...",
        "dish": {
            "id": 123,
            "name": "宫保鸡丁",
            "price": "15.00",
            "image": "http://example.com/dish.jpg",
            "canteen_name": "第一食堂"
        },
        "created_at": "2025-11-19T10:00:00Z",
        "likes_count": 5,
        "comments_count": 3,
        "is_liked": false,
        "comments": [
            {
                "id": 5,
                "author": {
                    "id": 2,
                    "username": "user2",
                    "nickname": "用户2",
                    "avatar": "http://example.com/avatar2.jpg"
                },
                "content": "这是一条顶级评论",
                "images": [
                    "http://example.com/comment_image.jpg"
                ],
                "parent": null,
                "created_at": "2025-11-19T10:02:00Z",
                "likes_count": 2,
                "is_liked": false,
                "replies": [
                    {
                        "id": 10,
                        "author": {
                            "id": 1,
                            "username": "user1",
                            "nickname": "用户1", 
                            "avatar": "http://example.com/avatar.jpg"
                        },
                        "content": "这是对上面评论的回复",
                        "images": [],
                        "parent": 5,
                        "created_at": "2025-11-19T10:05:00Z",
                        "likes_count": 0,
                        "is_liked": false
                    }
                ]
            }
        ]
    }
}
```

---

## 🎯 使用场景

### 1. 发布菜品相关帖子
```javascript
// 前端示例
const createPost = async (subject, content, dishId) => {
    const response = await axios.post('/api/v1/posts/create/', {
        subject,
        content,
        dish: dishId  // 关联菜品
    }, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.data;
};
```

### 2. 评论带图片
```javascript
const createComment = async (postId, content, images) => {
    const response = await axios.post('/api/v1/comments/create/', {
        post: postId,
        content,
        images  // 图片URL数组
    }, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.data;
};
```

### 3. 回复评论
```javascript
const replyToComment = async (postId, content, parentCommentId) => {
    const response = await axios.post('/api/v1/comments/create/', {
        post: postId,
        content,
        parent: parentCommentId  // 父评论ID
    }, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.data;
};
```

### 4. 查看菜品相关讨论
```javascript
const getDishPosts = async (dishId, page = 1) => {
    const response = await axios.get(`/api/v1/dishes/${dishId}/posts/?page=${page}`);
    return response.data;
};
```

---

## ⚠️ 注意事项

1. **图片限制**：每条评论最多可上传 9 张图片
2. **回复层级**：只支持两级结构（只能回复顶级评论）
3. **菜品关联**：帖子发布后菜品关联关系不能修改
4. **删除规则**：删除顶级评论会同时删除所有回复
5. **权限要求**：所有创建操作都需要用户登录

---

## 🚀 部署说明

1. **数据库迁移**：
   ```bash
   cd src/backend/app
   python manage.py makemigrations post
   python manage.py migrate post
   ```

2. **容器化部署**：
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

3. **创建超级用户**：
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **访问管理后台**：
   - URL: http://your-domain/admin/
   - 可以查看和管理所有帖子、评论、图片等数据

---

**功能已完整实现，可以开始测试！** 🎉