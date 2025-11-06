# Axios API 使用指南

本指南介绍如何在前端项目中使用 List API 的 axios 封装。

## 一、安装依赖

如果你的项目还没有安装 axios：

```bash
npm install axios
# 或
yarn add axios
```

## 二、引入 API 封装

### 方式一：直接引入（推荐）

```javascript
// 引入所有 API 函数
import {
  getCanteens,
  getCanteenDetail,
  getDishes,
  getDishDetail,
  rateDish,
  createReview,
  // ... 其他函数
} from '@/utils/api/listApi';
```

### 方式二：引入默认实例

如果需要自定义请求：

```javascript
import api from '@/utils/api/listApi';

// 自定义请求
const customRequest = async () => {
  const response = await api.get('/custom-endpoint');
  return response;
};
```

## 三、基础使用示例

### 1. 获取食堂列表

```javascript
import { getCanteens } from '@/utils/api/listApi';

async function fetchCanteens() {
  try {
    const response = await getCanteens({
      search: '第一', // 可选：搜索食堂名称
      ordering: 'name', // 可选：排序方式
    });

    console.log(response.data); // 食堂列表数组
    return response.data;
  } catch (error) {
    console.error('获取食堂列表失败:', error.message);
  }
}
```

### 2. 获取菜品列表

```javascript
import { getDishes } from '@/utils/api/listApi';

async function fetchDishes() {
  try {
    const response = await getDishes({
      canteen_id: 1, // 可选：按食堂筛选
      tag_ids: [1, 2], // 可选：按标签筛选
      min_rating: 4.0, // 可选：最低评分
      min_price: 10, // 可选：最低价格
      max_price: 50, // 可选：最高价格
      search: '宫保', // 可选：关键词搜索
      ordering: '-rating', // 可选：按评分降序
    });

    console.log(response.data); // 菜品列表数组
    return response.data;
  } catch (error) {
    console.error('获取菜品列表失败:', error.message);
  }
}
```

### 3. 获取菜品详情

```javascript
import { getDishDetail } from '@/utils/api/listApi';

async function fetchDishDetail(dishId) {
  try {
    const response = await getDishDetail(dishId);
    console.log(response.data); // 菜品详情对象
    return response.data;
  } catch (error) {
    console.error('获取菜品详情失败:', error.message);
  }
}
```

## 四、需要认证的接口

### 1. 先登录获取 Token

```javascript
// 假设你有登录接口
import loginApi from '@/utils/api/auth';

async function login(username, password) {
  try {
    const response = await loginApi.post('/login/', {
      username,
      password,
    });

    // 保存 token 到 localStorage
    localStorage.setItem('access_token', response.data.tokens.access);
    return response.data;
  } catch (error) {
    console.error('登录失败:', error.message);
  }
}
```

### 2. 给菜品评分（需要登录）

```javascript
import { rateDish } from '@/utils/api/listApi';

async function rate(dishId, rating) {
  try {
    const response = await rateDish(dishId, {
      rating: rating, // 0-5 之间的数字
    });

    console.log('评分成功:', response.message);
    console.log('新的评分:', response.data.new_rating);
    return response.data;
  } catch (error) {
    console.error('评分失败:', error.message);
    if (error.code === 401) {
      // Token 过期，需要重新登录
      console.error('请先登录');
    }
  }
}

// 使用示例
rate(1, 4.5);
```

### 3. 创建评论（需要登录）

```javascript
import { createReview } from '@/utils/api/listApi';

async function createComment(dishId, content, images = [], ratingScore = null) {
  try {
    const response = await createReview(dishId, {
      content, // 评论内容（至少5个字符）
      images, // 可选：图片URL数组（最多9张）
      rating_score: ratingScore, // 可选：评分 1.0-5.0
    });

    console.log('评论创建成功:', response.message);
    return response.data;
  } catch (error) {
    console.error('创建评论失败:', error.message);
    if (error.errors) {
      // 字段验证错误
      console.error('验证错误:', error.errors);
    }
  }
}

// 使用示例
createComment(1, '很好吃！推荐大家尝试。', ['http://example.com/food.jpg'], 4.5);
```

## 五、在 Vue/React 组件中使用

### Vue 3 Composition API 示例

```vue
<template>
  <div>
    <h1>食堂列表</h1>
    <ul>
      <li v-for="canteen in canteens" :key="canteen.id">
        {{ canteen.name }}
      </li>
    </ul>

    <h2>菜品列表</h2>
    <ul>
      <li v-for="dish in dishes" :key="dish.id">{{ dish.name }} - ¥{{ dish.price }}</li>
    </ul>

    <button @click="handleRate(1, 4.5)">给菜品评分</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getCanteens, getDishes, rateDish } from '@/utils/api/listApi';

const canteens = ref([]);
const dishes = ref([]);

// 获取食堂列表
const loadCanteens = async () => {
  try {
    const response = await getCanteens();
    canteens.value = response.data;
  } catch (error) {
    console.error('加载食堂列表失败:', error);
  }
};

// 获取菜品列表
const loadDishes = async () => {
  try {
    const response = await getDishes({
      ordering: '-rating',
    });
    dishes.value = response.data;
  } catch (error) {
    console.error('加载菜品列表失败:', error);
  }
};

// 给菜品评分
const handleRate = async (dishId, rating) => {
  try {
    await rateDish(dishId, { rating });
    alert('评分成功！');
    // 重新加载菜品列表以获取最新评分
    await loadDishes();
  } catch (error) {
    alert('评分失败: ' + error.message);
  }
};

// 组件挂载时加载数据
onMounted(() => {
  loadCanteens();
  loadDishes();
});
</script>
```

### React Hooks 示例

```jsx
import { useState, useEffect } from 'react';
import { getCanteens, getDishes, rateDish } from '@/utils/api/listApi';

function CanteenList() {
  const [canteens, setCanteens] = useState([]);
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(false);

  // 获取食堂列表
  const loadCanteens = async () => {
    setLoading(true);
    try {
      const response = await getCanteens();
      setCanteens(response.data);
    } catch (error) {
      console.error('加载食堂列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取菜品列表
  const loadDishes = async () => {
    try {
      const response = await getDishes({ ordering: '-rating' });
      setDishes(response.data);
    } catch (error) {
      console.error('加载菜品列表失败:', error);
    }
  };

  // 给菜品评分
  const handleRate = async (dishId, rating) => {
    try {
      await rateDish(dishId, { rating });
      alert('评分成功！');
      // 重新加载菜品列表
      await loadDishes();
    } catch (error) {
      alert('评分失败: ' + error.message);
    }
  };

  useEffect(() => {
    loadCanteens();
    loadDishes();
  }, []);

  if (loading) return <div>加载中...</div>;

  return (
    <div>
      <h1>食堂列表</h1>
      <ul>
        {canteens.map((canteen) => (
          <li key={canteen.id}>{canteen.name}</li>
        ))}
      </ul>

      <h2>菜品列表</h2>
      <ul>
        {dishes.map((dish) => (
          <li key={dish.id}>
            {dish.name} - ¥{dish.price}
            <button onClick={() => handleRate(dish.id, 4.5)}>评分</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CanteenList;
```

## 六、错误处理

### 统一错误处理

```javascript
import { getDishes } from '@/utils/api/listApi';

async function fetchDishesWithErrorHandling() {
  try {
    const response = await getDishes();
    return response.data;
  } catch (error) {
    // 根据错误代码处理
    switch (error.code) {
      case 400:
        console.error('请求参数错误:', error.message);
        break;
      case 401:
        console.error('未授权，请先登录');
        // 跳转到登录页
        // router.push('/login')
        break;
      case 403:
        console.error('没有权限:', error.message);
        break;
      case 404:
        console.error('资源不存在');
        break;
      case 500:
        console.error('服务器错误');
        break;
      default:
        console.error('请求失败:', error.message);
    }

    // 如果有字段验证错误
    if (error.errors) {
      Object.keys(error.errors).forEach((field) => {
        console.error(`${field}: ${error.errors[field]}`);
      });
    }

    throw error;
  }
}
```

## 七、配置 baseURL

如果你的后端地址不在同一域名，需要修改 `listApi.js` 中的 `baseURL`：

```javascript
// src/utils/api/listApi.js

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // 修改为实际后端地址
  timeout: 10000,
  // ...
});
```

或者使用环境变量：

```javascript
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api',
  timeout: 10000,
  // ...
});
```

## 八、完整使用示例

```javascript
import {
  getCanteens,
  getCanteenDetail,
  getDishes,
  getDishDetail,
  getHotDishes,
  getNewDishes,
  rateDish,
  addTagToDish,
  getTags,
  getReviews,
  createReview,
  updateReview,
  deleteReview,
  likeReview,
  getMyReviews,
} from '@/utils/api/listApi';

// 1. 获取食堂列表
const canteens = await getCanteens({ search: '第一' });

// 2. 获取食堂详情及菜品
const canteenDetail = await getCanteenDetail(1, {
  tag_ids: [1, 2],
  min_rating: 4.0,
  ordering: '-rating',
});

// 3. 获取菜品列表
const dishes = await getDishes({
  canteen_id: 1,
  tag_ids: [1],
  min_price: 10,
  max_price: 50,
  ordering: '-rating',
});

// 4. 获取菜品详情
const dish = await getDishDetail(1);

// 5. 获取热门菜品
const hotDishes = await getHotDishes({ limit: 10 });

// 6. 获取新品菜品
const newDishes = await getNewDishes({ limit: 10 });

// 7. 给菜品评分（需登录）
await rateDish(1, { rating: 4.5 });

// 8. 添加标签（需登录）
await addTagToDish(1, { tag_ids: [1, 2] });

// 9. 获取所有标签
const tags = await getTags();

// 10. 获取评论列表
const reviews = await getReviews(1, {
  search: '好吃',
  ordering: '-created_at',
});

// 11. 创建评论（需登录）
await createReview(1, {
  content: '很好吃！推荐大家尝试。',
  images: ['http://example.com/food.jpg'],
  rating_score: 4.5,
});

// 12. 更新评论（需登录）
await updateReview(1, {
  content: '更新后的评论内容',
});

// 13. 删除评论（需登录）
await deleteReview(1);

// 14. 点赞评论（需登录）
await likeReview(1);

// 15. 获取我的评论（需登录）
const myReviews = await getMyReviews();
```

## 九、类型定义（TypeScript）

如果你使用 TypeScript，可以创建类型定义文件：

```typescript
// src/types/listApi.d.ts

export interface Canteen {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Dish {
  id: number;
  name: string;
  description: string;
  price: string;
  image: string | null;
  canteen: number;
  canteen_name: string;
  tags: Tag[];
  rating: string;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: number;
  name: string;
  dish_count: number;
}

export interface Review {
  id: number;
  user: number;
  username: string;
  dish: number;
  dish_name: string;
  content: string;
  images: string[];
  user_rating: number | null;
  likes_count: number;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}
```

然后在 `listApi.js` 中使用这些类型（如果重命名为 `.ts` 文件）。

## 十、常见问题

### 1. CORS 错误

如果遇到 CORS 错误，需要配置后端允许跨域请求。或者在开发环境中使用代理：

```javascript
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
};
```

### 2. Token 过期

Token 过期时会返回 401 错误。可以在响应拦截器中处理：

```javascript
// 在 listApi.js 的响应拦截器中已处理
// 你也可以添加自定义处理逻辑
```

### 3. 数组参数传递

`tag_ids` 等数组参数，axios 会自动转换为 `tag_ids=1&tag_ids=2` 格式，无需手动处理。

---

现在你可以开始在前端项目中使用这些 API 了！如有问题，请参考 `docs/api/list-api-openapi.json` 中的接口文档。
