# 食堂消费数据功能 API 文档

## 功能概述

该功能允许用户绑定清华大学学号，并从清华一卡通系统自动获取食堂消费数据。系统会自动打开用户选择的浏览器，等待用户登录一卡通系统，然后自动获取认证cookie并爬取消费数据。

## 技术特点

1. **动态浏览器检测**：支持 Chrome、Firefox、Edge、Safari 四种浏览器
2. **自动认证**：自动获取servicehall cookie，无需用户手动复制
3. **数据解密**：自动解密一卡通系统返回的加密数据
4. **智能刷新**：优先使用已保存的cookie，失效时自动重新获取

## API 端点

### 1. 获取消费数据

**请求**
```
GET /api/v1/canteen/consumption/
Authorization: Bearer <jwt_token>
```

**响应 - 成功 (200)**
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "username": "testuser",
        "idserial": "2021012345",
        "total_amount": "1234.56",
        "canteen_count": 8,
        "canteen_data": {
            "观畴园": 456.78,
            "紫荆园": 345.67,
            "桃李园": 234.56,
            "听涛园": 123.45
        },
        "last_fetched": "2024-11-30T10:30:00Z",
        "created": "2024-11-01T08:00:00Z"
    }
}
```

**响应 - 未绑定 (404)**
```json
{
    "code": 404,
    "message": "未绑定学号，请先绑定",
    "data": null
}
```

---

### 2. 绑定学号

**请求**
```
POST /api/v1/canteen/bind/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "idserial": "2021012345",
    "browser_type": "chrome"  // 可选，默认chrome，支持: chrome, firefox, edge, safari
}
```

**功能说明**
- 系统会自动打开指定类型的浏览器
- 浏览器会导航到清华一卡通网站
- 用户需要在浏览器中手动登录
- 登录成功后，系统会自动检测并获取cookie
- 自动爬取并保存消费数据
- 浏览器会自动关闭

**响应 - 成功 (200)**
```json
{
    "code": 200,
    "message": "绑定成功",
    "data": {
        "idserial": "2021012345",
        "total_amount": 1234.56,
        "canteen_count": 8,
        "canteens": {
            "观畴园": 456.78,
            "紫荆园": 345.67,
            "桃李园": 234.56
        }
    }
}
```

**响应 - 失败 (500)**
```json
{
    "code": 500,
    "message": "超时：未能获取servicehall cookie，请确保已成功登录网站",
    "data": null
}
```

---

### 3. 刷新消费数据

**请求**
```
POST /api/v1/canteen/refresh/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "servicehall": "可选，提供新的cookie",
    "browser_type": "chrome"  // 可选，当需要重新获取cookie时使用
}
```

**功能说明**
- 优先使用系统已保存的cookie
- 如果cookie失效，会自动打开浏览器重新获取
- 可以手动提供新的cookie跳过浏览器登录

**响应 - 成功 (200)**
```json
{
    "code": 200,
    "message": "刷新成功",
    "data": {
        "idserial": "2021012345",
        "total_amount": 1250.00,
        "canteen_count": 8,
        "canteens": {
            "观畴园": 470.00,
            "紫荆园": 350.00
        }
    }
}
```

**响应 - 未绑定 (400)**
```json
{
    "code": 400,
    "message": "请先绑定学号",
    "data": null
}
```

---

### 4. 解绑学号

**请求**
```
DELETE /api/v1/canteen/unbind/
Authorization: Bearer <jwt_token>
```

**响应 - 成功 (200)**
```json
{
    "code": 200,
    "message": "解绑成功"
}
```

**响应 - 未绑定 (400)**
```json
{
    "code": 400,
    "message": "未绑定学号"
}
```

---

## 浏览器支持

### Chrome
- 默认选项
- 需要安装 ChromeDriver
- 下载地址：https://chromedriver.chromium.org/

### Firefox
- 需要安装 GeckoDriver
- 下载地址：https://github.com/mozilla/geckodriver/releases

### Edge
- 需要安装 EdgeDriver
- 下载地址：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

### Safari
- macOS内置支持
- 需在"偏好设置 > 高级"中启用"在菜单栏中显示开发菜单"
- 在"开发"菜单中启用"允许远程自动化"

---

## 部署说明

### 1. 安装依赖

```bash
# 在后端目录中
cd src/backend/app
pip install -r requirements_canteen.txt
```

### 2. 安装浏览器驱动

根据用户使用的浏览器，下载对应的驱动程序并添加到系统PATH中。

### 3. 执行数据库迁移

```bash
python manage.py makemigrations canteen
python manage.py migrate canteen
```

### 4. 创建超级用户（如需使用Admin）

```bash
python manage.py createsuperuser
```

---

## 使用流程

### 前端集成示例

```javascript
// 1. 绑定学号
async function bindCanteenAccount() {
    const response = await fetch('/api/v1/canteen/bind/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${jwt_token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            idserial: '2021012345',
            browser_type: 'chrome'  // 根据用户系统选择
        })
    });
    
    const result = await response.json();
    
    if (result.code === 200) {
        console.log('绑定成功，消费数据：', result.data);
        // 提示：浏览器已打开，请登录一卡通系统
    }
}

// 2. 获取消费数据
async function getConsumptionData() {
    const response = await fetch('/api/v1/canteen/consumption/', {
        headers: {
            'Authorization': `Bearer ${jwt_token}`
        }
    });
    
    const result = await response.json();
    
    if (result.code === 200) {
        displayConsumptionData(result.data);
    } else if (result.code === 404) {
        // 提示用户先绑定学号
        showBindPrompt();
    }
}

// 3. 刷新数据
async function refreshConsumptionData() {
    const response = await fetch('/api/v1/canteen/refresh/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${jwt_token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            browser_type: 'chrome'
        })
    });
    
    const result = await response.json();
    
    if (result.code === 200) {
        console.log('刷新成功：', result.data);
    }
}
```

---

## 数据模型

### CanteenConsumption

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user | ForeignKey | 关联用户 |
| idserial | String | 学号 |
| servicehall_cookie | String | 认证cookie（加密存储） |
| total_amount | Decimal | 总消费金额（元） |
| canteen_count | Integer | 消费过的食堂数量 |
| canteen_data | JSON | 各食堂消费详情 |
| last_fetched | DateTime | 最后更新时间 |
| created | DateTime | 创建时间 |

---

## 安全建议

1. **Cookie保护**：servicehall_cookie 在数据库中应加密存储
2. **HTTPS**：生产环境必须使用HTTPS传输
3. **频率限制**：建议对绑定和刷新接口添加频率限制
4. **超时设置**：浏览器登录等待时间默认5分钟，可根据需要调整
5. **日志记录**：记录所有爬取操作，便于审计

---

## 常见问题

### Q: 浏览器无法自动打开？
A: 确保已安装对应的浏览器驱动，并添加到系统PATH中。

### Q: Cookie失效怎么办？
A: 调用刷新接口，系统会自动重新打开浏览器获取新cookie。

### Q: 支持批量导入吗？
A: 当前版本每个用户只能绑定一个学号，如需批量功能可扩展。

### Q: 数据多久更新一次？
A: 需要用户手动调用刷新接口，建议前端实现自动刷新功能。

---

## 后续优化方向

1. ✅ 支持多种浏览器
2. ✅ 自动cookie管理
3. ⏳ Cookie加密存储
4. ⏳ 后台定时自动刷新
5. ⏳ 数据变化通知
6. ⏳ 消费趋势分析
7. ⏳ 食堂推荐功能

---

**版本**: 1.0.0  
**更新时间**: 2024-11-30  
**维护者**: 开发团队
