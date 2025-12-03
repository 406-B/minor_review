# Apifox 使用指南

本指南将帮助你在 Apifox 中配置和使用 List API。

## 一、导入 OpenAPI 文档到 Apifox

### 方法一：直接导入 OpenAPI JSON 文件

1. **打开 Apifox**
   - 启动 Apifox 应用

2. **创建新项目（可选）**
   - 点击左侧 "项目" → "新建项目"
   - 项目名称：`Minor Review - List API`
   - 项目描述：`食堂、菜品、标签、评论相关 API`

3. **导入 OpenAPI 文档**
   - 点击项目 → "导入" → "OpenAPI"
   - 选择文件：`docs/api/list-api-openapi.json`
   - 点击 "导入"
   - Apifox 会自动解析并创建所有接口

### 方法二：通过 URL 导入（如果文件托管在服务器）

1. 在 Apifox 中选择 "导入" → "OpenAPI"
2. 选择 "URL" 标签
3. 输入 OpenAPI 文档的 URL
4. 点击 "导入"

## 二、配置环境变量

### 1. 创建环境

1. 点击顶部 "环境管理" 或右侧环境切换按钮
2. 点击 "新建环境"
3. 创建以下环境：

   **开发环境（Development）**
   - 环境名称：`开发环境`
   - 变量：
     - `baseURL`: `http://localhost:8000`
     - `apiPrefix`: `/api`

   **生产环境（Production）**
   - 环境名称：`生产环境`
   - 变量：
     - `baseURL`: `https://api.example.com`
     - `apiPrefix`: `/api`

### 2. 配置前置脚本（可选）

在环境设置中，可以添加前置脚本来自动获取 token：

```javascript
// 自动获取 token（如果已登录）
const token = pm.environment.get('access_token');
if (token) {
  pm.request.headers.add({
    key: 'Authorization',
    value: `Bearer ${token}`,
  });
}
```

## 三、配置全局认证

### 方法一：在接口级别配置（推荐）

1. 打开需要认证的接口（如 `POST /dishes/{dish_id}/rate/`）
2. 点击 "认证" 标签
3. 选择 "Bearer Token"
4. Token 值：可以从环境变量中读取 `{{access_token}}`

### 方法二：在环境配置中设置

1. 进入环境管理
2. 在环境变量中添加：
   - `access_token`: 你的 JWT token
3. 在接口的 Header 中引用：`Authorization: Bearer {{access_token}}`

## 四、测试接口

### 1. 测试公开接口（无需认证）

例如测试 `GET /api/canteens/`：

1. 打开接口 `GET /canteens/`
2. 点击 "发送"
3. 查看响应结果

### 2. 测试需要认证的接口

例如测试 `POST /api/dishes/1/rate/`：

1. **先登录获取 token**
   - 如果你的项目有登录接口，先调用登录接口
   - 将返回的 token 保存到环境变量 `access_token` 中

2. **配置认证**
   - 在接口的 "认证" 标签中选择 Bearer Token
   - 或者手动在 Headers 中添加：`Authorization: Bearer {{access_token}}`

3. **设置请求参数**
   - 在 Body 中填入：
     ```json
     {
       "rating": 4.5
     }
     ```

4. **发送请求**
   - 点击 "发送"
   - 查看响应结果

## 五、分享 API 文档给前端

### 方法一：在线文档链接

1. 在 Apifox 中点击 "分享" → "在线文档"
2. 配置文档信息：
   - 文档名称：`Minor Review - List API 文档`
   - 可见范围：选择团队成员或公开
3. 生成文档链接
4. 将链接分享给前端开发人员

### 方法二：导出文档

1. 点击 "导出" → "HTML"
2. 选择导出的接口范围
3. 导出后发送给前端团队

## 六、生成前端代码

Apifox 支持生成前端请求代码：

1. 打开任意接口
2. 点击右侧 "代码" 按钮
3. 选择代码类型：
   - **JavaScript (Axios)**
   - **TypeScript (Axios)**
   - **JavaScript (Fetch)**
   - 等等
4. 复制生成的代码到前端项目

示例（生成 Axios 代码）：

```javascript
import axios from 'axios';

const response = await axios.get('http://localhost:8000/api/canteens/', {
  params: {
    search: '',
    ordering: 'name',
  },
});
```

## 七、常用接口快速测试

### 1. 获取食堂列表

- 接口：`GET /api/canteens/`
- 认证：无需
- 参数：`{ search?: string, ordering?: string }`

### 2. 获取菜品列表

- 接口：`GET /api/dishes/`
- 认证：无需
- 参数：`{ canteen_id?, tag_ids?, min_rating?, search?, ordering? }`

### 3. 给菜品评分（需登录）

- 接口：`POST /api/dishes/{dish_id}/rate/`
- 认证：需要 Bearer Token
- Body：`{ "rating": 4.5 }`

### 4. 创建评论（需登录）

- 接口：`POST /api/dishes/{dish_id}/reviews/create/`
- 认证：需要 Bearer Token
- Body：
  ```json
  {
    "content": "很好吃！",
    "images": ["http://example.com/1.jpg"],
    "rating_score": 4.5
  }
  ```

### 5. 获取用户偏好标签（需登录）

- 接口：`GET /api/profile/preference-tags`
- 认证：需要 Bearer Token
- 参数：无

### 6. 设置用户偏好标签（需登录）

- 接口：`POST /api/profile/preference-tags/set`
- 认证：需要 Bearer Token
- Body：
  ```json
  {
    "tag_ids": [1, 2, 3, 5]
  }
  ```
- 说明：会覆盖原有偏好标签

### 7. 添加用户偏好标签（需登录）

- 接口：`POST /api/profile/preference-tags/add`
- 认证：需要 Bearer Token
- Body：
  ```json
  {
    "tag_ids": [6, 7]
  }
  ```
- 说明：追加到原有偏好标签

### 8. 获取个性化推荐菜品（需登录）

- 接口：`GET /api/profile/recommended-dishes`
- 认证：需要 Bearer Token
- 参数：
  - `latitude`: 用户纬度（可选）
  - `longitude`: 用户经度（可选）
  - `page`: 页码，默认 1
  - `page_size`: 每页数量，默认 20
- 示例：`GET /api/profile/recommended-dishes?latitude=39.9042&longitude=116.4074&page=1&page_size=20`

### 9. 获取附近推荐菜品（需登录）

- 接口：`GET /api/profile/nearby-dishes`
- 认证：需要 Bearer Token
- 参数：
  - `latitude`: 用户纬度（必需）
  - `longitude`: 用户经度（必需）
  - `page`: 页码，默认 1
  - `page_size`: 每页数量，默认 20
- 示例：`GET /api/profile/nearby-dishes?latitude=39.9042&longitude=116.4074`

## 八、注意事项

1. **Token 获取**：需要先通过登录接口获取 token，然后设置到环境变量中
2. **CORS 配置**：如果前端和后端不在同一域名，需要配置 CORS
3. **接口路径**：确保 baseURL 和接口路径正确拼接
4. **错误处理**：所有接口返回格式为 `{ code, message, data }`，code 200 表示成功
5. **数组参数**：`tag_ids` 等数组参数需要使用 `tag_ids=1&tag_ids=2` 格式

## 九、与前端协作

### 前端如何使用这些 API：

1. **使用我们提供的 axios 封装**：

   ```javascript
   import { getCanteens, rateDish } from '@/utils/api/listApi';

   // 获取食堂列表
   const result = await getCanteens({ search: '第一' });
   console.log(result.data); // 食堂列表数据

   // 给菜品评分
   await rateDish(1, { rating: 4.5 });
   ```

2. **或直接使用 Apifox 生成的代码**

3. **查看在线文档**：前端可以通过你分享的文档链接查看所有接口说明

## 十、更新 API 文档

如果后端接口有更新：

1. 更新 `docs/api/list-api-openapi.json` 文件
2. 在 Apifox 中重新导入或手动更新接口
3. 重新分享文档链接给前端

---

## 快速开始清单

- [ ] 导入 `docs/api/list-api-openapi.json` 到 Apifox
- [ ] 创建开发环境和生产环境
- [ ] 配置环境变量 `baseURL` 和 `apiPrefix`
- [ ] 测试一个公开接口（如 `GET /api/canteens/`）
- [ ] 获取登录 token 并设置到环境变量
- [ ] 测试一个需要认证的接口（如 `POST /api/dishes/1/rate/`）
- [ ] 生成在线文档链接并分享给前端
- [ ] 前端安装并使用 `src/utils/api/listApi.js` 中的封装函数

完成以上步骤后，你就可以在 Apifox 中管理和测试所有 List API 接口了！
