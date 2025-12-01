---
title: Minor Review - List API
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.30"

---

# Minor Review - List API

API documentation for List module (Canteens, Dishes, Tags, Reviews)

Base URLs:

Email: <a href="mailto:support@example.com">API Support</a> 

# Authentication

- HTTP Authentication, scheme: bearer<br/>使用 Bearer Token 认证，格式：Authorization: Bearer <token>

# Canteens

<a id="opIdgetCanteens"></a>

## GET 获取食堂列表

GET /canteens/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|search|query|string| 否 |搜索食堂名称|
|ordering|query|string| 否 |排序方式|

#### 枚举值

|属性|值|
|---|---|
|ordering|name|
|ordering|-name|
|ordering|created_at|
|ordering|-created_at|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取食堂列表成功",
  "data": [
    {
      "id": 1,
      "name": "第一食堂",
      "latitude": 39.9042,
      "longitude": 116.4074,
      "address": "校园东区",
      "distance": 523.5,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ]
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|false|none||none|
|» message|string|false|none||none|
|» data|[[Canteen](#schemacanteen)]|false|none||none|
|»» id|integer|false|none||none|
|»» name|string|false|none||none|
|»» latitude|number(float)¦null|false|none||纬度|
|»» longitude|number(float)¦null|false|none||经度|
|»» address|string|false|none||食堂地址|
|»» distance|number(float)¦null|false|none||距离用户的距离（米），仅在提供位置信息时返回|
|»» created_at|string(date-time)|false|none||none|
|»» updated_at|string(date-time)|false|none||none|

<a id="opIdgetCanteenDetail"></a>

## GET 获取食堂详情及菜品

GET /canteens/{canteen_id}/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|canteen_id|path|integer| 是 |none|
|tag_ids|query|array[integer]| 否 |按标签筛选（可多个）|
|min_rating|query|number| 否 |最低评分|
|search|query|string| 否 |关键词搜索|
|ordering|query|string| 否 |none|

#### 枚举值

|属性|值|
|---|---|
|ordering|rating|
|ordering|-rating|
|ordering|view_count|
|ordering|-view_count|
|ordering|price|
|ordering|-price|
|ordering|name|
|ordering|-name|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取食堂详情成功",
  "data": {
    "canteen": {
      "id": 1,
      "name": "第一食堂",
      "latitude": 39.9042,
      "longitude": 116.4074,
      "address": "校园东区",
      "distance": 523.5,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    },
    "dishes": [
      {
        "id": 0,
        "name": "string",
        "price": "string",
        "image": "string",
        "canteen_name": "string",
        "tags": [
          {
            "id": null,
            "name": null,
            "dish_count": null,
            "created_at": null,
            "updated_at": null
          }
        ],
        "rating": "string",
        "view_count": 0,
        "distance": 0.1,
        "matched_tags_count": 0
      }
    ],
    "dish_count": 20
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[CanteenDetailResponse](#schemacanteendetailresponse)|

# Dishes

<a id="opIdgetDishes"></a>

## GET 获取菜品列表

GET /dishes/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|canteen_id|query|integer| 否 |按食堂筛选|
|tag_ids|query|array[integer]| 否 |按标签筛选（可多个）|
|min_rating|query|number| 否 |最低评分|
|min_price|query|number| 否 |最低价格|
|max_price|query|number| 否 |最高价格|
|search|query|string| 否 |关键词搜索|
|ordering|query|string| 否 |none|

#### 枚举值

|属性|值|
|---|---|
|ordering|rating|
|ordering|-rating|
|ordering|view_count|
|ordering|-view_count|
|ordering|price|
|ordering|-price|
|ordering|name|
|ordering|-name|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取菜品列表成功",
  "data": [
    {
      "id": 0,
      "name": "string",
      "price": "string",
      "image": "string",
      "canteen_name": "string",
      "tags": [
        {
          "id": 1,
          "name": "辣",
          "dish_count": 10,
          "created_at": "2019-08-24T14:15:22Z",
          "updated_at": "2019-08-24T14:15:22Z"
        }
      ],
      "rating": "string",
      "view_count": 0,
      "distance": 0.1,
      "matched_tags_count": 0
    }
  ]
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[DishListResponse](#schemadishlistresponse)|

<a id="opIdgetDishDetail"></a>

## GET 获取菜品详情

GET /dishes/{dish_id}/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|dish_id|path|integer| 是 |none|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取菜品详情成功",
  "data": {
    "id": 1,
    "name": "宫保鸡丁",
    "description": "经典川菜，麻辣鲜香",
    "price": "12.50",
    "image": "http://example.com/image.jpg",
    "canteen": 1,
    "canteen_name": "第一食堂",
    "tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "pending_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "has_pending_tags": false,
    "rating": "4.5",
    "view_count": 100,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[DishDetailResponse](#schemadishdetailresponse)|

<a id="opIdgetHotDishes"></a>

## GET 获取热门菜品

GET /dishes/hot/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|limit|query|integer| 否 |返回数量|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取菜品列表成功",
  "data": [
    {
      "id": 0,
      "name": "string",
      "price": "string",
      "image": "string",
      "canteen_name": "string",
      "tags": [
        {
          "id": 1,
          "name": "辣",
          "dish_count": 10,
          "created_at": "2019-08-24T14:15:22Z",
          "updated_at": "2019-08-24T14:15:22Z"
        }
      ],
      "rating": "string",
      "view_count": 0,
      "distance": 0.1,
      "matched_tags_count": 0
    }
  ]
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[DishListResponse](#schemadishlistresponse)|

<a id="opIdgetNewDishes"></a>

## GET 获取新品菜品

GET /dishes/new/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|limit|query|integer| 否 |返回数量|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取菜品列表成功",
  "data": [
    {
      "id": 0,
      "name": "string",
      "price": "string",
      "image": "string",
      "canteen_name": "string",
      "tags": [
        {
          "id": 1,
          "name": "辣",
          "dish_count": 10,
          "created_at": "2019-08-24T14:15:22Z",
          "updated_at": "2019-08-24T14:15:22Z"
        }
      ],
      "rating": "string",
      "view_count": 0,
      "distance": 0.1,
      "matched_tags_count": 0
    }
  ]
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[DishListResponse](#schemadishlistresponse)|

<a id="opIdrateDish"></a>

## POST 给菜品评分

POST /dishes/{dish_id}/rate/

> Body 请求参数

```json
{
  "rating": 4.5
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|dish_id|path|integer| 是 |none|
|body|body|object| 是 |none|
|» rating|body|number| 是 |none|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "评分成功",
  "data": {
    "dish_id": 1,
    "new_rating": 4.5
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[RateResponse](#schemarateresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|

<a id="opIdaddTagToDish"></a>

## POST 给菜品添加标签

POST /dishes/{dish_id}/tags/

> Body 请求参数

```json
{
  "tag_ids": [
    1,
    2,
    3
  ],
  "tag_name": "新标签名称"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|dish_id|path|integer| 是 |none|
|body|body|object| 是 |none|
|» tag_ids|body|[integer]| 否 |none|
|» tag_name|body|string| 否 |none|
|» *anonymous*|body|object| 否 |none|
|» *anonymous*|body|object| 否 |none|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取菜品详情成功",
  "data": {
    "id": 1,
    "name": "宫保鸡丁",
    "description": "经典川菜，麻辣鲜香",
    "price": "12.50",
    "image": "http://example.com/image.jpg",
    "canteen": 1,
    "canteen_name": "第一食堂",
    "tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "pending_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "has_pending_tags": false,
    "rating": "4.5",
    "view_count": 100,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[DishDetailResponse](#schemadishdetailresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|

<a id="opIdapprovePendingTags"></a>

## POST 批准待审核标签（管理员）

POST /dishes/{dish_id}/tags/approve/

> Body 请求参数

```json
{
  "tag_ids": [
    1,
    2
  ]
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|dish_id|path|integer| 是 |none|
|body|body|object| 否 |none|
|» tag_ids|body|[integer]| 否 |要批准的标签ID列表，留空则批准所有|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取菜品详情成功",
  "data": {
    "id": 1,
    "name": "宫保鸡丁",
    "description": "经典川菜，麻辣鲜香",
    "price": "12.50",
    "image": "http://example.com/image.jpg",
    "canteen": 1,
    "canteen_name": "第一食堂",
    "tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "pending_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "has_pending_tags": false,
    "rating": "4.5",
    "view_count": 100,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[DishDetailResponse](#schemadishdetailresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|无权限|None|

<a id="opIdrejectPendingTags"></a>

## POST 拒绝待审核标签（管理员）

POST /dishes/{dish_id}/tags/reject/

> Body 请求参数

```json
{
  "tag_ids": [
    1,
    2
  ]
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|dish_id|path|integer| 是 |none|
|body|body|object| 是 |none|
|» tag_ids|body|[integer]| 是 |none|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取菜品详情成功",
  "data": {
    "id": 1,
    "name": "宫保鸡丁",
    "description": "经典川菜，麻辣鲜香",
    "price": "12.50",
    "image": "http://example.com/image.jpg",
    "canteen": 1,
    "canteen_name": "第一食堂",
    "tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "pending_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "has_pending_tags": false,
    "rating": "4.5",
    "view_count": 100,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[DishDetailResponse](#schemadishdetailresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|无权限|None|

# Tags

<a id="opIdgetTags"></a>

## GET 获取所有标签

GET /tags/

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取标签列表成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ]
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[TagListResponse](#schemataglistresponse)|

<a id="opIdcreateTag"></a>

## POST 创建新标签（管理员）

POST /tags/create/

> Body 请求参数

```json
{
  "name": "辣"
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 是 |none|
|» name|body|string| 是 |none|

> 返回示例

> 201 Response

```json
{
  "code": 201,
  "message": "标签创建成功",
  "data": {
    "id": 1,
    "name": "辣",
    "dish_count": 10,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|创建成功|[TagResponse](#schematagresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|无权限|None|

# Reviews

<a id="opIdgetReviews"></a>

## GET 获取菜品评论列表

GET /dishes/{dish_id}/reviews/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|dish_id|path|integer| 是 |none|
|search|query|string| 否 |搜索评论内容或用户名|
|ordering|query|string| 否 |none|

#### 枚举值

|属性|值|
|---|---|
|ordering|created_at|
|ordering|-created_at|
|ordering|likes_count|
|ordering|-likes_count|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取评论列表成功",
  "data": {
    "reviews": [
      {
        "id": 1,
        "user": 1,
        "username": "user123",
        "dish": 1,
        "dish_name": "宫保鸡丁",
        "content": "很好吃！",
        "images": [
          "http://example.com/1.jpg"
        ],
        "user_rating": 4.5,
        "likes_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "total": 10
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[ReviewListResponse](#schemareviewlistresponse)|

<a id="opIdcreateReview"></a>

## POST 创建评论

POST /dishes/{dish_id}/reviews/create/

> Body 请求参数

```json
{
  "content": "很好吃！",
  "images": [
    "http://example.com/1.jpg"
  ],
  "rating_score": 4.5
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|dish_id|path|integer| 是 |none|
|body|body|object| 是 |none|
|» content|body|string| 是 |none|
|» images|body|[string]| 否 |none|
|» rating_score|body|number| 否 |可选，如果提供则同时创建或更新评分|

> 返回示例

> 201 Response

```json
{
  "code": 201,
  "message": "评论创建成功",
  "data": {
    "id": 1,
    "user": 1,
    "username": "user123",
    "dish": 1,
    "dish_name": "宫保鸡丁",
    "content": "很好吃！",
    "images": [
      "http://example.com/1.jpg"
    ],
    "user_rating": 4.5,
    "likes_count": 10,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|创建成功|[ReviewResponse](#schemareviewresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|

<a id="opIdupdateReview"></a>

## PUT 更新评论

PUT /reviews/{review_id}/

> Body 请求参数

```json
{
  "content": "更新后的内容",
  "images": [
    "http://example.com/new.jpg"
  ]
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|review_id|path|integer| 是 |none|
|body|body|object| 否 |none|
|» content|body|string| 否 |none|
|» images|body|[string]| 否 |none|

> 返回示例

> 200 Response

```json
{
  "code": 201,
  "message": "评论创建成功",
  "data": {
    "id": 1,
    "user": 1,
    "username": "user123",
    "dish": 1,
    "dish_name": "宫保鸡丁",
    "content": "很好吃！",
    "images": [
      "http://example.com/1.jpg"
    ],
    "user_rating": 4.5,
    "likes_count": 10,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|更新成功|[ReviewResponse](#schemareviewresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|无权限|None|

<a id="opIdpatchReview"></a>

## PATCH 部分更新评论

PATCH /reviews/{review_id}/

> Body 请求参数

```json
{
  "content": "string",
  "images": [
    "http://example.com"
  ]
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|review_id|path|integer| 是 |none|
|body|body|object| 否 |none|
|» content|body|string| 否 |none|
|» images|body|[string]| 否 |none|

> 返回示例

> 200 Response

```json
{
  "code": 201,
  "message": "评论创建成功",
  "data": {
    "id": 1,
    "user": 1,
    "username": "user123",
    "dish": 1,
    "dish_name": "宫保鸡丁",
    "content": "很好吃！",
    "images": [
      "http://example.com/1.jpg"
    ],
    "user_rating": 4.5,
    "likes_count": 10,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|更新成功|[ReviewResponse](#schemareviewresponse)|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|无权限|None|

<a id="opIddeleteReview"></a>

## DELETE 删除评论

DELETE /reviews/{review_id}/delete/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|review_id|path|integer| 是 |none|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "评论删除成功"
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|删除成功|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|无权限|None|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|false|none||none|
|» message|string|false|none||none|

<a id="opIdlikeReview"></a>

## POST 点赞/取消点赞评论

POST /reviews/{review_id}/like/

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|review_id|path|integer| 是 |none|

> 返回示例

> 200 Response

```json
{
  "code": 201,
  "message": "评论创建成功",
  "data": {
    "id": 1,
    "user": 1,
    "username": "user123",
    "dish": 1,
    "dish_name": "宫保鸡丁",
    "content": "很好吃！",
    "images": [
      "http://example.com/1.jpg"
    ],
    "user_rating": 4.5,
    "likes_count": 10,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[ReviewResponse](#schemareviewresponse)|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|

<a id="opIdgetMyReviews"></a>

## GET 获取我的评论

GET /reviews/my/

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取评论列表成功",
  "data": {
    "reviews": [
      {
        "id": 1,
        "user": 1,
        "username": "user123",
        "dish": 1,
        "dish_name": "宫保鸡丁",
        "content": "很好吃！",
        "images": [
          "http://example.com/1.jpg"
        ],
        "user_rating": 4.5,
        "likes_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "total": 10
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[ReviewListResponse](#schemareviewlistresponse)|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|

# Profile

<a id="opIdgetPreferenceTags"></a>

## GET 获取用户偏好标签

GET /profile/preference-tags

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取偏好标签成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ]
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[PreferenceTagsResponse](#schemapreferencetagsresponse)|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|

<a id="opIdsetPreferenceTags"></a>

## POST 设置用户偏好标签（覆盖模式）

POST /profile/preference-tags/set

> Body 请求参数

```json
{
  "tag_ids": [
    1,
    2,
    3,
    5
  ]
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 是 |none|
|» tag_ids|body|[integer]| 是 |none|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取偏好标签成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ]
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|设置成功|[PreferenceTagsResponse](#schemapreferencetagsresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|

<a id="opIdaddPreferenceTags"></a>

## POST 添加用户偏好标签（追加模式）

POST /profile/preference-tags/add

> Body 请求参数

```json
{
  "tag_ids": [
    6,
    7
  ]
}
```

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|body|body|object| 是 |none|
|» tag_ids|body|[integer]| 是 |none|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取偏好标签成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ]
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|添加成功|[PreferenceTagsResponse](#schemapreferencetagsresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|

<a id="opIdgetRecommendedDishes"></a>

## GET 获取个性化推荐菜品

GET /profile/recommended-dishes

根据用户偏好标签和位置（可选）综合推荐菜品，优先推荐距离近且匹配偏好的菜品

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|latitude|query|number(float)| 否 |用户纬度（可选，提供后按距离优先排序）|
|longitude|query|number(float)| 否 |用户经度（可选，提供后按距离优先排序）|
|page|query|integer| 否 |页码|
|page_size|query|integer| 否 |每页数量|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取推荐菜品成功",
  "data": {
    "dishes": [
      {
        "id": 0,
        "name": "string",
        "price": "string",
        "image": "string",
        "canteen_name": "string",
        "tags": [
          {
            "id": null,
            "name": null,
            "dish_count": null,
            "created_at": null,
            "updated_at": null
          }
        ],
        "rating": "string",
        "view_count": 0,
        "distance": 0.1,
        "matched_tags_count": 0
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20,
    "user_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "location_enabled": true
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[RecommendedDishesResponse](#schemarecommendeddishesresponse)|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|用户未设置偏好标签|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|false|none||none|
|» message|string|false|none||none|
|» data|object|false|none||none|
|»» dishes|[[DishListItem](#schemadishlistitem)]|false|none||none|
|»»» id|integer|false|none||none|
|»»» name|string|false|none||none|
|»»» price|string(decimal)|false|none||none|
|»»» image|string¦null|false|none||none|
|»»» canteen_name|string|false|none||none|
|»»» tags|[[Tag](#schematag)]|false|none||none|
|»»»» id|integer|false|none||none|
|»»»» name|string|false|none||none|
|»»»» dish_count|integer|false|none||none|
|»»»» created_at|string(date-time)|false|none||none|
|»»»» updated_at|string(date-time)|false|none||none|
|»»» rating|string(decimal)|false|none||none|
|»»» view_count|integer|false|none||none|
|»»» distance|number(float)¦null|false|none||距离用户的距离（米），仅在个性化推荐中返回|
|»»» matched_tags_count|integer¦null|false|none||匹配的标签数量，仅在个性化推荐中返回|
|»» total|integer|false|none||none|
|»» page|integer|false|none||none|
|»» page_size|integer|false|none||none|
|»» user_tags|[[Tag](#schematag)]|false|none||none|
|»»» id|integer|false|none||none|
|»»» name|string|false|none||none|
|»»» dish_count|integer|false|none||none|
|»»» created_at|string(date-time)|false|none||none|
|»»» updated_at|string(date-time)|false|none||none|
|»» location_enabled|boolean|false|none||是否启用了位置排序|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|false|none||none|
|» message|string|false|none||none|
|» data|null|false|none||none|

<a id="opIdgetNearbyRecommendedDishes"></a>

## GET 获取附近推荐菜品

GET /profile/nearby-dishes

根据用户位置找到最近的食堂，推荐该食堂中匹配用户偏好的菜品

### 请求参数

|名称|位置|类型|必选|说明|
|---|---|---|---|---|
|latitude|query|number(float)| 是 |用户纬度|
|longitude|query|number(float)| 是 |用户经度|
|page|query|integer| 否 |页码|
|page_size|query|integer| 否 |每页数量|

> 返回示例

> 200 Response

```json
{
  "code": 200,
  "message": "获取附近推荐菜品成功",
  "data": {
    "nearest_canteen": {
      "id": 1,
      "name": "第一食堂",
      "address": "校园东区",
      "distance": 523.5,
      "latitude": 39.9042,
      "longitude": 116.4074
    },
    "nearby_canteens": [
      {
        "id": 0,
        "name": "string",
        "address": "string",
        "distance": 0.1
      }
    ],
    "dishes": [
      {
        "id": 0,
        "name": "string",
        "price": "string",
        "image": "string",
        "canteen_name": "string",
        "tags": [
          {
            "id": null,
            "name": null,
            "dish_count": null,
            "created_at": null,
            "updated_at": null
          }
        ],
        "rating": "string",
        "view_count": 0,
        "distance": 0.1,
        "matched_tags_count": 0
      }
    ],
    "total": 30,
    "page": 1,
    "page_size": 20,
    "user_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ]
  }
}
```

### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|[NearbyDishesResponse](#schemanearbydishesresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|请求参数错误|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|未认证|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|暂无食堂位置信息|Inline|

### 返回数据结构

状态码 **200**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|false|none||none|
|» message|string|false|none||none|
|» data|object|false|none||none|
|»» nearest_canteen|object|false|none||none|
|»»» id|integer|false|none||none|
|»»» name|string|false|none||none|
|»»» address|string|false|none||none|
|»»» distance|number(float)|false|none||距离用户的距离（米）|
|»»» latitude|number(float)|false|none||none|
|»»» longitude|number(float)|false|none||none|
|»» nearby_canteens|[object]|false|none||附近的食堂列表（前5个）|
|»»» id|integer|false|none||none|
|»»» name|string|false|none||none|
|»»» address|string|false|none||none|
|»»» distance|number(float)|false|none||none|
|»» dishes|[[DishListItem](#schemadishlistitem)]|false|none||none|
|»»» id|integer|false|none||none|
|»»» name|string|false|none||none|
|»»» price|string(decimal)|false|none||none|
|»»» image|string¦null|false|none||none|
|»»» canteen_name|string|false|none||none|
|»»» tags|[[Tag](#schematag)]|false|none||none|
|»»»» id|integer|false|none||none|
|»»»» name|string|false|none||none|
|»»»» dish_count|integer|false|none||none|
|»»»» created_at|string(date-time)|false|none||none|
|»»»» updated_at|string(date-time)|false|none||none|
|»»» rating|string(decimal)|false|none||none|
|»»» view_count|integer|false|none||none|
|»»» distance|number(float)¦null|false|none||距离用户的距离（米），仅在个性化推荐中返回|
|»»» matched_tags_count|integer¦null|false|none||匹配的标签数量，仅在个性化推荐中返回|
|»» total|integer|false|none||none|
|»» page|integer|false|none||none|
|»» page_size|integer|false|none||none|
|»» user_tags|[[Tag](#schematag)]|false|none||none|
|»»» id|integer|false|none||none|
|»»» name|string|false|none||none|
|»»» dish_count|integer|false|none||none|
|»»» created_at|string(date-time)|false|none||none|
|»»» updated_at|string(date-time)|false|none||none|

状态码 **404**

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» code|integer|false|none||none|
|» message|string|false|none||none|

# 数据模型

<h2 id="tocS_Canteen">Canteen</h2>

<a id="schemacanteen"></a>
<a id="schema_Canteen"></a>
<a id="tocScanteen"></a>
<a id="tocscanteen"></a>

```json
{
  "id": 1,
  "name": "第一食堂",
  "latitude": 39.9042,
  "longitude": 116.4074,
  "address": "校园东区",
  "distance": 523.5,
  "created_at": "2019-08-24T14:15:22Z",
  "updated_at": "2019-08-24T14:15:22Z"
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|id|integer|false|none||none|
|name|string|false|none||none|
|latitude|number(float)¦null|false|none||纬度|
|longitude|number(float)¦null|false|none||经度|
|address|string|false|none||食堂地址|
|distance|number(float)¦null|false|none||距离用户的距离（米），仅在提供位置信息时返回|
|created_at|string(date-time)|false|none||none|
|updated_at|string(date-time)|false|none||none|

<h2 id="tocS_Tag">Tag</h2>

<a id="schematag"></a>
<a id="schema_Tag"></a>
<a id="tocStag"></a>
<a id="tocstag"></a>

```json
{
  "id": 1,
  "name": "辣",
  "dish_count": 10,
  "created_at": "2019-08-24T14:15:22Z",
  "updated_at": "2019-08-24T14:15:22Z"
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|id|integer|false|none||none|
|name|string|false|none||none|
|dish_count|integer|false|none||none|
|created_at|string(date-time)|false|none||none|
|updated_at|string(date-time)|false|none||none|

<h2 id="tocS_Dish">Dish</h2>

<a id="schemadish"></a>
<a id="schema_Dish"></a>
<a id="tocSdish"></a>
<a id="tocsdish"></a>

```json
{
  "id": 1,
  "name": "宫保鸡丁",
  "description": "经典川菜，麻辣鲜香",
  "price": "12.50",
  "image": "http://example.com/image.jpg",
  "canteen": 1,
  "canteen_name": "第一食堂",
  "tags": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ],
  "pending_tags": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ],
  "has_pending_tags": false,
  "rating": "4.5",
  "view_count": 100,
  "created_at": "2019-08-24T14:15:22Z",
  "updated_at": "2019-08-24T14:15:22Z"
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|id|integer|false|none||none|
|name|string|false|none||none|
|description|string|false|none||none|
|price|string(decimal)|false|none||none|
|image|string(uri)¦null|false|none||none|
|canteen|integer|false|none||none|
|canteen_name|string|false|none||none|
|tags|[[Tag](#schematag)]|false|none||none|
|pending_tags|[[Tag](#schematag)]|false|none||none|
|has_pending_tags|boolean|false|none||none|
|rating|string(decimal)|false|none||none|
|view_count|integer|false|none||none|
|created_at|string(date-time)|false|none||none|
|updated_at|string(date-time)|false|none||none|

<h2 id="tocS_DishListItem">DishListItem</h2>

<a id="schemadishlistitem"></a>
<a id="schema_DishListItem"></a>
<a id="tocSdishlistitem"></a>
<a id="tocsdishlistitem"></a>

```json
{
  "id": 0,
  "name": "string",
  "price": "string",
  "image": "string",
  "canteen_name": "string",
  "tags": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ],
  "rating": "string",
  "view_count": 0,
  "distance": 0.1,
  "matched_tags_count": 0
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|id|integer|false|none||none|
|name|string|false|none||none|
|price|string(decimal)|false|none||none|
|image|string¦null|false|none||none|
|canteen_name|string|false|none||none|
|tags|[[Tag](#schematag)]|false|none||none|
|rating|string(decimal)|false|none||none|
|view_count|integer|false|none||none|
|distance|number(float)¦null|false|none||距离用户的距离（米），仅在个性化推荐中返回|
|matched_tags_count|integer¦null|false|none||匹配的标签数量，仅在个性化推荐中返回|

<h2 id="tocS_Review">Review</h2>

<a id="schemareview"></a>
<a id="schema_Review"></a>
<a id="tocSreview"></a>
<a id="tocsreview"></a>

```json
{
  "id": 1,
  "user": 1,
  "username": "user123",
  "dish": 1,
  "dish_name": "宫保鸡丁",
  "content": "很好吃！",
  "images": [
    "http://example.com/1.jpg"
  ],
  "user_rating": 4.5,
  "likes_count": 10,
  "created_at": "2019-08-24T14:15:22Z",
  "updated_at": "2019-08-24T14:15:22Z"
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|id|integer|false|none||none|
|user|integer|false|none||none|
|username|string|false|none||none|
|dish|integer|false|none||none|
|dish_name|string|false|none||none|
|content|string|false|none||none|
|images|[string]|false|none||none|
|user_rating|number¦null|false|none||none|
|likes_count|integer|false|none||none|
|created_at|string(date-time)|false|none||none|
|updated_at|string(date-time)|false|none||none|

<h2 id="tocS_CanteenDetailResponse">CanteenDetailResponse</h2>

<a id="schemacanteendetailresponse"></a>
<a id="schema_CanteenDetailResponse"></a>
<a id="tocScanteendetailresponse"></a>
<a id="tocscanteendetailresponse"></a>

```json
{
  "code": 200,
  "message": "获取食堂详情成功",
  "data": {
    "canteen": {
      "id": 1,
      "name": "第一食堂",
      "latitude": 39.9042,
      "longitude": 116.4074,
      "address": "校园东区",
      "distance": 523.5,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    },
    "dishes": [
      {
        "id": 0,
        "name": "string",
        "price": "string",
        "image": "string",
        "canteen_name": "string",
        "tags": [
          {
            "id": null,
            "name": null,
            "dish_count": null,
            "created_at": null,
            "updated_at": null
          }
        ],
        "rating": "string",
        "view_count": 0,
        "distance": 0.1,
        "matched_tags_count": 0
      }
    ],
    "dish_count": 20
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|object|false|none||none|
|» canteen|[Canteen](#schemacanteen)|false|none||none|
|» dishes|[[DishListItem](#schemadishlistitem)]|false|none||none|
|» dish_count|integer|false|none||none|

<h2 id="tocS_DishListResponse">DishListResponse</h2>

<a id="schemadishlistresponse"></a>
<a id="schema_DishListResponse"></a>
<a id="tocSdishlistresponse"></a>
<a id="tocsdishlistresponse"></a>

```json
{
  "code": 200,
  "message": "获取菜品列表成功",
  "data": [
    {
      "id": 0,
      "name": "string",
      "price": "string",
      "image": "string",
      "canteen_name": "string",
      "tags": [
        {
          "id": 1,
          "name": "辣",
          "dish_count": 10,
          "created_at": "2019-08-24T14:15:22Z",
          "updated_at": "2019-08-24T14:15:22Z"
        }
      ],
      "rating": "string",
      "view_count": 0,
      "distance": 0.1,
      "matched_tags_count": 0
    }
  ]
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|[[DishListItem](#schemadishlistitem)]|false|none||none|

<h2 id="tocS_DishDetailResponse">DishDetailResponse</h2>

<a id="schemadishdetailresponse"></a>
<a id="schema_DishDetailResponse"></a>
<a id="tocSdishdetailresponse"></a>
<a id="tocsdishdetailresponse"></a>

```json
{
  "code": 200,
  "message": "获取菜品详情成功",
  "data": {
    "id": 1,
    "name": "宫保鸡丁",
    "description": "经典川菜，麻辣鲜香",
    "price": "12.50",
    "image": "http://example.com/image.jpg",
    "canteen": 1,
    "canteen_name": "第一食堂",
    "tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "pending_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "has_pending_tags": false,
    "rating": "4.5",
    "view_count": 100,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|[Dish](#schemadish)|false|none||none|

<h2 id="tocS_TagListResponse">TagListResponse</h2>

<a id="schemataglistresponse"></a>
<a id="schema_TagListResponse"></a>
<a id="tocStaglistresponse"></a>
<a id="tocstaglistresponse"></a>

```json
{
  "code": 200,
  "message": "获取标签列表成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ]
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|[[Tag](#schematag)]|false|none||none|

<h2 id="tocS_TagResponse">TagResponse</h2>

<a id="schematagresponse"></a>
<a id="schema_TagResponse"></a>
<a id="tocStagresponse"></a>
<a id="tocstagresponse"></a>

```json
{
  "code": 201,
  "message": "标签创建成功",
  "data": {
    "id": 1,
    "name": "辣",
    "dish_count": 10,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|[Tag](#schematag)|false|none||none|

<h2 id="tocS_RateResponse">RateResponse</h2>

<a id="schemarateresponse"></a>
<a id="schema_RateResponse"></a>
<a id="tocSrateresponse"></a>
<a id="tocsrateresponse"></a>

```json
{
  "code": 200,
  "message": "评分成功",
  "data": {
    "dish_id": 1,
    "new_rating": 4.5
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|object|false|none||none|
|» dish_id|integer|false|none||none|
|» new_rating|number|false|none||none|

<h2 id="tocS_ReviewListResponse">ReviewListResponse</h2>

<a id="schemareviewlistresponse"></a>
<a id="schema_ReviewListResponse"></a>
<a id="tocSreviewlistresponse"></a>
<a id="tocsreviewlistresponse"></a>

```json
{
  "code": 200,
  "message": "获取评论列表成功",
  "data": {
    "reviews": [
      {
        "id": 1,
        "user": 1,
        "username": "user123",
        "dish": 1,
        "dish_name": "宫保鸡丁",
        "content": "很好吃！",
        "images": [
          "http://example.com/1.jpg"
        ],
        "user_rating": 4.5,
        "likes_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "total": 10
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|object|false|none||none|
|» reviews|[[Review](#schemareview)]|false|none||none|
|» total|integer|false|none||none|

<h2 id="tocS_ReviewResponse">ReviewResponse</h2>

<a id="schemareviewresponse"></a>
<a id="schema_ReviewResponse"></a>
<a id="tocSreviewresponse"></a>
<a id="tocsreviewresponse"></a>

```json
{
  "code": 201,
  "message": "评论创建成功",
  "data": {
    "id": 1,
    "user": 1,
    "username": "user123",
    "dish": 1,
    "dish_name": "宫保鸡丁",
    "content": "很好吃！",
    "images": [
      "http://example.com/1.jpg"
    ],
    "user_rating": 4.5,
    "likes_count": 10,
    "created_at": "2019-08-24T14:15:22Z",
    "updated_at": "2019-08-24T14:15:22Z"
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|[Review](#schemareview)|false|none||none|

<h2 id="tocS_Error">Error</h2>

<a id="schemaerror"></a>
<a id="schema_Error"></a>
<a id="tocSerror"></a>
<a id="tocserror"></a>

```json
{
  "code": 400,
  "message": "错误信息",
  "errors": {}
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|errors|object|false|none||字段验证错误详情|

<h2 id="tocS_PreferenceTagsResponse">PreferenceTagsResponse</h2>

<a id="schemapreferencetagsresponse"></a>
<a id="schema_PreferenceTagsResponse"></a>
<a id="tocSpreferencetagsresponse"></a>
<a id="tocspreferencetagsresponse"></a>

```json
{
  "code": 200,
  "message": "获取偏好标签成功",
  "data": [
    {
      "id": 1,
      "name": "辣",
      "dish_count": 10,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z"
    }
  ]
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|[[Tag](#schematag)]|false|none||none|

<h2 id="tocS_RecommendedDishesResponse">RecommendedDishesResponse</h2>

<a id="schemarecommendeddishesresponse"></a>
<a id="schema_RecommendedDishesResponse"></a>
<a id="tocSrecommendeddishesresponse"></a>
<a id="tocsrecommendeddishesresponse"></a>

```json
{
  "code": 200,
  "message": "获取推荐菜品成功",
  "data": {
    "dishes": [
      {
        "id": 0,
        "name": "string",
        "price": "string",
        "image": "string",
        "canteen_name": "string",
        "tags": [
          {
            "id": null,
            "name": null,
            "dish_count": null,
            "created_at": null,
            "updated_at": null
          }
        ],
        "rating": "string",
        "view_count": 0,
        "distance": 0.1,
        "matched_tags_count": 0
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20,
    "user_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ],
    "location_enabled": true
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|object|false|none||none|
|» dishes|[[DishListItem](#schemadishlistitem)]|false|none||none|
|» total|integer|false|none||none|
|» page|integer|false|none||none|
|» page_size|integer|false|none||none|
|» user_tags|[[Tag](#schematag)]|false|none||none|
|» location_enabled|boolean|false|none||是否启用了位置排序|

<h2 id="tocS_NearbyDishesResponse">NearbyDishesResponse</h2>

<a id="schemanearbydishesresponse"></a>
<a id="schema_NearbyDishesResponse"></a>
<a id="tocSnearbydishesresponse"></a>
<a id="tocsnearbydishesresponse"></a>

```json
{
  "code": 200,
  "message": "获取附近推荐菜品成功",
  "data": {
    "nearest_canteen": {
      "id": 1,
      "name": "第一食堂",
      "address": "校园东区",
      "distance": 523.5,
      "latitude": 39.9042,
      "longitude": 116.4074
    },
    "nearby_canteens": [
      {
        "id": 0,
        "name": "string",
        "address": "string",
        "distance": 0.1
      }
    ],
    "dishes": [
      {
        "id": 0,
        "name": "string",
        "price": "string",
        "image": "string",
        "canteen_name": "string",
        "tags": [
          {
            "id": null,
            "name": null,
            "dish_count": null,
            "created_at": null,
            "updated_at": null
          }
        ],
        "rating": "string",
        "view_count": 0,
        "distance": 0.1,
        "matched_tags_count": 0
      }
    ],
    "total": 30,
    "page": 1,
    "page_size": 20,
    "user_tags": [
      {
        "id": 1,
        "name": "辣",
        "dish_count": 10,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
      }
    ]
  }
}

```

### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|code|integer|false|none||none|
|message|string|false|none||none|
|data|object|false|none||none|
|» nearest_canteen|object|false|none||none|
|»» id|integer|false|none||none|
|»» name|string|false|none||none|
|»» address|string|false|none||none|
|»» distance|number(float)|false|none||距离用户的距离（米）|
|»» latitude|number(float)|false|none||none|
|»» longitude|number(float)|false|none||none|
|» nearby_canteens|[object]|false|none||附近的食堂列表（前5个）|
|»» id|integer|false|none||none|
|»» name|string|false|none||none|
|»» address|string|false|none||none|
|»» distance|number(float)|false|none||none|
|» dishes|[[DishListItem](#schemadishlistitem)]|false|none||none|
|» total|integer|false|none||none|
|» page|integer|false|none||none|
|» page_size|integer|false|none||none|
|» user_tags|[[Tag](#schematag)]|false|none||none|

