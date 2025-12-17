# 美食日历 API 文档

## 概述

美食日历功能用于记录和展示用户的菜品打卡历史。用户可以查看最近7天或按月查看打卡的菜品记录。

## API 端点

### 1. 获取用户打卡历史（按日期范围）

**端点**: `GET /api/v1/profile/check-in-history`

**描述**: 获取指定日期范围内的打卡历史记录

**请求参数**:
- `start_date` (string, 可选): 开始日期，格式 `YYYY-MM-DD`，默认为当前日期前6天
- `end_date` (string, 可选): 结束日期，格式 `YYYY-MM-DD`，默认为当前日期
- `year` (integer, 可选): 年份，用于按月查询
- `month` (integer, 可选): 月份（1-12），用于按月查询

**请求头**:
```
Authorization: Bearer <jwt_token>
```

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "check_ins": [
      {
        "date": "2025-12-12",
        "dishes": [
          {
            "id": 1,
            "name": "红烧肉",
            "image": "/media/dishes/hongshaorou.jpg",
            "canteen_name": "第一食堂",
            "window_name": "风味窗口",
            "price": 15.0,
            "rating": 4.5,
            "check_in_time": "2025-12-12T12:30:00Z",
            "check_in_count": 5,
            "total_consumption": 75.0,
            "achievement_tier": "silver",
            "tags": [
              {"id": 1, "name": "肉类"},
              {"id": 2, "name": "经典"}
            ]
          }
        ]
      },
      {
        "date": "2025-12-11",
        "dishes": []
      }
    ],
    "summary": {
      "total_check_ins": 15,
      "total_dishes": 8,
      "total_consumption": 200.0,
      "most_frequent_dish": {
        "id": 1,
        "name": "红烧肉",
        "count": 5
      }
    }
  }
}
```

**响应字段说明**:

- `check_ins`: 打卡记录数组
  - `date`: 日期 (YYYY-MM-DD)
  - `dishes`: 当天打卡的菜品列表
    - `id`: 菜品ID
    - `name`: 菜品名称
    - `image`: 菜品图片URL
    - `canteen_name`: 所属食堂名称
    - `window_name`: 所属窗口名称
    - `price`: 菜品价格
    - `rating`: 菜品评分
    - `check_in_time`: 打卡时间（ISO 8601格式）
    - `check_in_count`: 该菜品累计打卡次数
    - `total_consumption`: 该菜品累计消费金额
    - `achievement_tier`: 成就等级 (`bronze`, `silver`, `gold`, `rainbow`)
    - `tags`: 菜品标签数组

- `summary`: 统计摘要
  - `total_check_ins`: 总打卡次数
  - `total_dishes`: 不同菜品数量
  - `total_consumption`: 总消费金额
  - `most_frequent_dish`: 最常打卡的菜品

**错误响应**:
```json
{
  "code": 401,
  "message": "未授权，请先登录"
}
```

```json
{
  "code": 400,
  "message": "日期格式错误"
}
```

### 2. 获取月度打卡概览

**端点**: `GET /api/v1/profile/check-in-calendar`

**描述**: 获取指定月份的打卡日历数据，用于快速查看哪些日期有打卡记录

**请求参数**:
- `year` (integer, 必需): 年份
- `month` (integer, 必需): 月份（1-12）

**请求头**:
```
Authorization: Bearer <jwt_token>
```

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "year": 2025,
    "month": 12,
    "check_in_dates": [
      {
        "date": "2025-12-01",
        "count": 2
      },
      {
        "date": "2025-12-12",
        "count": 1
      }
    ]
  }
}
```

**响应字段说明**:
- `year`: 年份
- `month`: 月份
- `check_in_dates`: 有打卡记录的日期数组
  - `date`: 日期 (YYYY-MM-DD)
  - `count`: 当天打卡的菜品数量

## 成就等级说明

菜品的成就等级根据打卡次数确定：

- `bronze` (铜色/本科): 1-2次打卡
- `silver` (银色/硕士): 3-5次打卡
- `gold` (金色/博士): 6-10次打卡
- `rainbow` (彩虹/院士): 11次及以上打卡

## 前端使用示例

### 获取最近7天打卡历史
```javascript
import { getCheckInHistory } from '@/api/foodCalendar'

const last7Days = await getCheckInHistory({
  start_date: '2025-12-06',
  end_date: '2025-12-12'
})
```

### 获取指定月份打卡历史
```javascript
const monthData = await getCheckInHistory({
  year: 2025,
  month: 12
})
```

### 获取月度概览（快速查看）
```javascript
import { getCheckInCalendar } from '@/api/foodCalendar'

const calendar = await getCheckInCalendar(2025, 12)
```

## 注意事项

1. 所有接口都需要用户登录认证（JWT Token）
2. 日期格式统一使用 ISO 8601 标准（YYYY-MM-DD）
3. 时间字段使用 ISO 8601 完整格式（带时区）
4. 图片URL为相对路径，前端需要拼接域名
5. 成就等级根据 `check_in_count` 字段动态计算
6. 价格和消费金额保留两位小数
