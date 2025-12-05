# 食堂消费数据功能

## 功能简介

这是一个集成到Django后端的食堂消费数据爬取功能，可以从清华大学一卡通系统自动获取用户的食堂消费记录。

## 主要特性

- ✅ **多浏览器支持**：支持 Chrome、Firefox、Edge、Safari
- ✅ **自动认证**：自动打开浏览器获取认证cookie
- ✅ **数据解密**：自动解密一卡通系统的加密数据
- ✅ **智能刷新**：Cookie失效时自动重新获取
- ✅ **RESTful API**：完整的CRUD接口
- ✅ **Admin后台**：支持Django Admin管理

## 目录结构

```
canteen/
├── __init__.py
├── admin.py              # Django Admin配置
├── apps.py               # 应用配置
├── models.py             # 数据模型（CanteenConsumption）
├── serializers.py        # DRF序列化器
├── services.py           # 爬取服务（浏览器自动化、数据解密）
├── controllers.py        # 业务逻辑控制器
├── views.py              # API视图
├── urls.py               # URL路由
├── tests.py              # 测试文件
└── migrations/           # 数据库迁移文件
```

## 快速开始

### 1. 安装依赖

```bash
cd src/backend/app
pip install -r requirements_canteen.txt
```

需要的包：
- `requests` - HTTP请求
- `pycryptodome` - AES解密
- `selenium` - 浏览器自动化

### 2. 安装浏览器驱动

根据用户使用的浏览器，下载对应驱动：

- **Chrome**: [ChromeDriver](https://chromedriver.chromium.org/)
- **Firefox**: [GeckoDriver](https://github.com/mozilla/geckodriver/releases)
- **Edge**: [EdgeDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
- **Safari**: macOS内置，需在系统设置中启用远程自动化

将驱动程序添加到系统PATH中。

### 3. 执行数据库迁移

**Windows**:
```bash
migrate_canteen.bat
```

**Linux/macOS**:
```bash
chmod +x migrate_canteen.sh
./migrate_canteen.sh
```

或手动执行：
```bash
python manage.py makemigrations canteen
python manage.py migrate canteen
```

### 4. 启动服务器

```bash
python manage.py runserver
```

## API使用示例

### 绑定学号并获取数据

```bash
curl -X POST http://localhost:8000/api/v1/canteen/bind/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "idserial": "2021012345",
    "browser_type": "chrome"
  }'
```

系统会自动：
1. 打开Chrome浏览器
2. 导航到一卡通网站
3. 等待用户登录（最多5分钟）
4. 自动获取cookie
5. 爬取并保存消费数据
6. 关闭浏览器

### 查看消费数据

```bash
curl http://localhost:8000/api/v1/canteen/consumption/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 刷新数据

```bash
curl -X POST http://localhost:8000/api/v1/canteen/refresh/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "browser_type": "chrome"
  }'
```

### 解绑学号

```bash
curl -X DELETE http://localhost:8000/api/v1/canteen/unbind/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 与原auto_login.py的区别

### 原文件特点
- ✅ 独立Python脚本
- ❌ 仅支持Chrome浏览器
- ❌ 命令行调用，不集成到后端
- ❌ 需要手动管理cookie

### 新实现特点
- ✅ 完全集成到Django后端
- ✅ 支持4种主流浏览器
- ✅ RESTful API接口
- ✅ 自动cookie管理
- ✅ 数据持久化
- ✅ Django Admin支持
- ✅ JWT认证保护

## 核心改进

### 1. 动态浏览器检测

原代码：
```python
driver = webdriver.Chrome(options=chrome_options)
```

新实现：
```python
def get_browser_driver(browser_type: str = 'chrome'):
    if browser_type == 'chrome':
        return webdriver.Chrome(options=ChromeOptions())
    elif browser_type == 'firefox':
        return webdriver.Firefox(options=FirefoxOptions())
    elif browser_type == 'edge':
        return webdriver.Edge(options=EdgeOptions())
    elif browser_type == 'safari':
        return webdriver.Safari()
```

### 2. 模块化设计

- `services.py` - 底层爬取服务
- `controllers.py` - 业务逻辑
- `views.py` - API接口
- `models.py` - 数据持久化

### 3. 自动Cookie管理

系统会自动：
- 保存获取的cookie
- 检测cookie是否失效
- 失效时自动重新获取

## 数据模型

```python
class CanteenConsumption(models.Model):
    user = models.OneToOneField(User)      # 关联用户
    idserial = models.CharField()          # 学号
    servicehall_cookie = models.CharField() # Cookie
    total_amount = models.DecimalField()   # 总消费
    canteen_count = models.IntegerField()  # 食堂数量
    canteen_data = models.JSONField()      # 详细数据
    last_fetched = models.DateTimeField()  # 更新时间
```

## 安全说明

1. **认证保护**：所有API都需要JWT认证
2. **数据隔离**：每个用户只能访问自己的数据
3. **Cookie加密**：建议在生产环境中加密存储cookie
4. **HTTPS传输**：生产环境必须使用HTTPS

## 测试

```bash
# 运行测试
python manage.py test canteen

# 检查代码
python manage.py check canteen
```

## 常见问题

### Q: 浏览器无法启动？
A: 检查浏览器驱动是否正确安装并在PATH中。

### Q: 登录超时？
A: 默认等待5分钟，可在`services.py`中调整`max_wait_time`参数。

### Q: Cookie失效？
A: 调用刷新接口，系统会自动重新获取。

### Q: 如何选择浏览器？
A: 前端可根据用户操作系统自动选择，或提供选项让用户选择。

## 完整文档

详细API文档请查看：`docs/CANTEEN_API.md`

## 贡献

欢迎提交Issue和Pull Request！

## 许可

MIT License
