# 食堂消费自动登录 API 文档

## 概述

本文档描述了食堂消费数据获取的自动登录功能，该功能使用 Selenium WebDriver 自动完成清华大学统一身份认证登录流程，并获取 `servicehall` cookie 用于后续的食堂消费数据爬取。

## 功能特性

- **后端自动化登录**：使用 Selenium 在后端自动完成登录流程
- **无头模式支持**：可在无图形界面的服务器环境运行
- **验证码处理**：支持前端输入验证码进行人机验证
- **多浏览器支持**：支持 Chrome、Firefox、Edge 浏览器
- **会话管理**：使用 session_id 管理多个并发登录请求
- **错误检测**：自动检测用户名密码错误、验证码错误等情况

## 工作流程

```
1. 前端调用 [启动自动登录] API
   └─→ 后端创建 session_id 并启动 Selenium 线程
       └─→ 自动填写用户名密码
           └─→ 检测是否需要验证码
               ├─→ 无需验证码：直接登录成功，返回 cookie
               └─→ 需要验证码：
                   ├─→ 前端调用 [提交验证码] API
                   │   └─→ 后端自动输入验证码并提交
                   │       └─→ 检测验证码是否正确
                   │           ├─→ 正确：处理确认界面，返回 cookie
                   │           └─→ 错误：返回错误信息
                   └─→ 前端调用 [查询登录状态] API 轮询结果
```

## API 端点列表

### 1. 启动自动登录

**端点**: `POST /api/v1/canteen/auto-login/start/`

**描述**: 启动自动登录流程，创建 Selenium 会话并自动填写用户名密码。

**请求体**:
```json
{
  "username": "2021012345",
  "password": "your_password",
  "browser": "chrome",
  "headless": true
}
```

**参数说明**:
- `username` (必填): 清华大学学号
- `password` (必填): INFO 密码
- `browser` (可选): 浏览器类型，可选值为 `chrome`、`firefox`、`edge`，默认为 `chrome`
- `headless` (可选): 是否使用无头模式，默认为 `true`

**响应示例**:

情况1：需要验证码
```json
{
  "session_id": "abc123def456",
  "status": "waiting_verification",
  "message": "请输入验证码"
}
```

情况2：直接登录成功（无需验证码）
```json
{
  "session_id": "abc123def456",
  "status": "completed",
  "cookie": "servicehall=xxxxxxxxxxxx",
  "message": "登录成功，已获取 cookie"
}
```

情况3：登录失败
```json
{
  "session_id": "abc123def456",
  "status": "failed",
  "error": "您的用户名或密码不正确"
}
```

**状态码**:
- `200`: 成功启动登录流程
- `400`: 参数错误或浏览器不支持
- `500`: 服务器内部错误

---

### 2. 提交验证码

**端点**: `POST /api/v1/canteen/auto-login/submit-code/`

**描述**: 向指定的登录会话提交验证码。

**请求体**:
```json
{
  "session_id": "abc123def456",
  "verification_code": "1234"
}
```

**参数说明**:
- `session_id` (必填): 登录会话 ID，由启动登录接口返回
- `verification_code` (必填): 4位数字验证码

**响应示例**:

成功提交:
```json
{
  "message": "验证码已提交"
}
```

会话不存在:
```json
{
  "error": "会话不存在或已过期"
}
```

会话状态错误:
```json
{
  "error": "会话状态不正确"
}
```

**状态码**:
- `200`: 验证码提交成功
- `400`: 参数错误或会话状态不正确
- `404`: 会话不存在

---

### 3. 查询登录状态

**端点**: `GET /api/v1/canteen/auto-login/status/?session_id=abc123def456`

**描述**: 查询指定登录会话的当前状态。

**查询参数**:
- `session_id` (必填): 登录会话 ID

**响应示例**:

等待验证码:
```json
{
  "status": "waiting_verification",
  "message": "等待验证码输入"
}
```

登录中:
```json
{
  "status": "processing",
  "message": "正在处理登录..."
}
```

登录成功:
```json
{
  "status": "completed",
  "cookie": "servicehall=xxxxxxxxxxxx",
  "message": "登录成功"
}
```

登录失败:
```json
{
  "status": "failed",
  "error": "验证码错误，请重试"
}
```

**状态码**:
- `200`: 成功获取状态
- `400`: 缺少 session_id 参数
- `404`: 会话不存在

**注意**: 
- 前端应每隔 2-3 秒轮询此接口，直到状态变为 `completed` 或 `failed`
- 当状态为 `completed` 时，会话会被自动清理，后续查询将返回 404

---

### 4. 使用 Cookie 获取消费数据

**端点**: `POST /api/v1/canteen/fetch-with-cookie/`

**描述**: 使用已获取的 `servicehall` cookie 直接获取食堂消费数据，不存储到数据库。

**请求体**:
```json
{
  "cookie": "servicehall=xxxxxxxxxxxx"
}
```

**参数说明**:
- `cookie` (必填): servicehall cookie 值

**响应示例**:

成功:
```json
{
  "message": "成功获取消费数据",
  "data": {
    "rows": [
      {
        "DEALTIME": "2024-01-15 12:30:00",
        "ACCNAME": "清芬园食堂",
        "MERCNAME": "一层窗口1",
        "TXAMT": "-15.50",
        "POSNAME": "一卡通消费"
      }
    ],
    "total": 150
  }
}
```

失败:
```json
{
  "error": "获取消费数据失败",
  "details": "Invalid cookie"
}
```

**状态码**:
- `200`: 成功获取数据
- `400`: Cookie 参数缺失
- `500`: 获取数据失败

---

## 错误处理

### 常见错误类型

| 错误信息 | 说明 | 解决方案 |
|---------|------|---------|
| `您的用户名或密码不正确` | 用户名或密码错误 | 检查用户名和密码是否正确 |
| `验证码错误，请重试` | 输入的验证码不正确 | 重新获取验证码并输入 |
| `浏览器不支持` | 指定的浏览器不可用 | 确保服务器已安装对应浏览器和 WebDriver |
| `初始化浏览器失败` | 浏览器启动失败 | 检查浏览器和 WebDriver 安装是否正确 |
| `会话不存在或已过期` | session_id 无效 | 重新调用启动登录接口 |
| `未找到登录按钮` | 页面元素定位失败 | 网站页面结构可能已变化，需要更新 XPath |

---

## 技术实现细节

### XPath 选择器

登录流程中使用的关键 XPath 选择器：

| 元素 | XPath | 说明 |
|-----|-------|------|
| 用户名输入框 | `//*[@id="i_user"]` | 学号输入 |
| 密码输入框 | `//*[@id="i_pass"]` | 密码输入 |
| 登录按钮 | `//*[@id="theform"]/div[5]/a` | 提交登录表单 |
| 验证码输入框 | `//*[@id="vericode"]` | 4位数字验证码 |
| 验证方式单选（手机） | `//input[@name="type" and @value="mobile"]` | 首次确认界面 |
| 首次确认按钮 | `//button[@type="submit" and contains(@class, "btn-info")]` | 提交验证方式 |
| 二次确认单选（否） | `//input[@name="type" and @value="否"]` | 第二次确认界面 |
| 二次确认按钮 | `//button[@type="button" and contains(@class, "btn-info")]` | 最终确认 |
| 密码错误提示 | `//div[@class="msg_note"]` | 检测密码错误 |
| 验证码错误提示 | `//div[@class="invalid-feedback"]` | 检测验证码错误 |

### 会话管理

- 使用全局字典 `LOGIN_SESSIONS` 存储所有活动会话
- 每个会话包含：
  - `driver`: Selenium WebDriver 实例
  - `status`: 会话状态（`waiting_verification`、`processing`、`completed`、`failed`）
  - `cookie`: 获取到的 servicehall cookie（仅在成功时）
  - `error`: 错误信息（仅在失败时）
  - `verification_code`: 前端提交的验证码
- 使用 `threading.Lock` 确保并发安全
- 会话在完成或失败后会自动清理

### 线程模型

- 主线程接收 API 请求并立即返回 session_id
- 后台 daemon 线程执行实际的登录流程
- 前端通过轮询 `/status/` 端点获取登录进度

### Cookie 获取

- 目标 URL: `https://card.tsinghua.edu.cn/`
- Cookie 名称: `servicehall`
- Cookie 有效期: 通常为 24 小时
- 检测方式: 每 0.5 秒检查一次，最多等待 20 秒

---

## 使用示例

### Python 示例（使用 requests）

```python
import requests
import time

# 1. 启动自动登录
response = requests.post(
    'http://localhost:8000/api/v1/canteen/auto-login/start/',
    json={
        'username': '2021012345',
        'password': 'your_password',
        'browser': 'chrome',
        'headless': True
    }
)
result = response.json()
session_id = result['session_id']

# 2. 检查是否需要验证码
if result['status'] == 'waiting_verification':
    # 获取用户输入验证码
    verification_code = input("请输入验证码: ")
    
    # 提交验证码
    requests.post(
        'http://localhost:8000/api/v1/canteen/auto-login/submit-code/',
        json={
            'session_id': session_id,
            'verification_code': verification_code
        }
    )
    
    # 3. 轮询登录状态
    while True:
        response = requests.get(
            f'http://localhost:8000/api/v1/canteen/auto-login/status/',
            params={'session_id': session_id}
        )
        status_result = response.json()
        
        if status_result['status'] == 'completed':
            cookie = status_result['cookie']
            print(f"登录成功，cookie: {cookie}")
            break
        elif status_result['status'] == 'failed':
            print(f"登录失败: {status_result.get('error')}")
            break
        
        time.sleep(2)  # 每2秒查询一次

elif result['status'] == 'completed':
    # 直接登录成功
    cookie = result['cookie']
    print(f"登录成功，cookie: {cookie}")

# 4. 使用 cookie 获取消费数据
response = requests.post(
    'http://localhost:8000/api/v1/canteen/fetch-with-cookie/',
    json={'cookie': cookie}
)
data = response.json()
print(f"获取到 {data['data']['total']} 条消费记录")
```

### JavaScript 示例（使用 fetch）

```javascript
// 1. 启动自动登录
const startLogin = async () => {
  const response = await fetch('/api/v1/canteen/auto-login/start/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: '2021012345',
      password: 'your_password',
      browser: 'chrome',
      headless: true
    })
  });
  
  const result = await response.json();
  return result;
};

// 2. 提交验证码
const submitCode = async (sessionId, code) => {
  await fetch('/api/v1/canteen/auto-login/submit-code/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      verification_code: code
    })
  });
};

// 3. 轮询登录状态
const pollStatus = async (sessionId) => {
  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      const response = await fetch(
        `/api/v1/canteen/auto-login/status/?session_id=${sessionId}`
      );
      const result = await response.json();
      
      if (result.status === 'completed') {
        clearInterval(interval);
        resolve(result.cookie);
      } else if (result.status === 'failed') {
        clearInterval(interval);
        reject(new Error(result.error));
      }
    }, 2000);
  });
};

// 4. 完整流程
const autoLogin = async () => {
  try {
    const startResult = await startLogin();
    
    if (startResult.status === 'waiting_verification') {
      const code = prompt('请输入验证码:');
      await submitCode(startResult.session_id, code);
      const cookie = await pollStatus(startResult.session_id);
      console.log('登录成功，cookie:', cookie);
    } else if (startResult.status === 'completed') {
      console.log('登录成功，cookie:', startResult.cookie);
    }
  } catch (error) {
    console.error('登录失败:', error.message);
  }
};
```

---

## 安全建议

1. **HTTPS**: 生产环境必须使用 HTTPS 传输敏感信息
2. **速率限制**: 建议对登录接口实施速率限制，防止暴力破解
3. **会话过期**: 建议实现会话超时机制，自动清理长时间未完成的会话
4. **日志记录**: 记录登录尝试和失败原因，便于审计和调试
5. **密码安全**: 不要在日志中记录明文密码
6. **Cookie 安全**: servicehall cookie 应安全存储，不应暴露给不可信的客户端

---

## 常见问题

### Q: 为什么需要验证码？
A: 清华大学统一身份认证系统会根据登录行为判断是否需要人机验证，通常从新IP或新设备登录时会要求输入验证码。

### Q: 无头模式会影响功能吗？
A: 不会。无头模式仅是不显示浏览器窗口，所有功能与有头模式完全相同。

### Q: 支持同时进行多个登录吗？
A: 支持。每个登录请求都有独立的 session_id 和 WebDriver 实例，互不干扰。

### Q: Cookie 有效期是多久？
A: 通常为 24 小时，过期后需要重新登录获取。

### Q: 如果网站页面结构变化怎么办？
A: 需要更新 `services.py` 中的 XPath 选择器以适应新的页面结构。

---

## 更新日志

### v1.0.0 (2024-01-15)
- ✅ 实现基本的自动登录功能
- ✅ 支持 Chrome、Firefox、Edge 浏览器
- ✅ 支持无头模式运行
- ✅ 实现验证码处理机制
- ✅ 添加密码错误检测
- ✅ 添加验证码错误检测
- ✅ 实现会话管理和并发支持
- ✅ 添加四个 REST API 端点

---

## 联系与支持

如有问题或建议，请联系开发团队或提交 Issue。
