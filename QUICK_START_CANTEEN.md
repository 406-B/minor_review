# 食堂消费数据功能 - 快速开始指南

## 🚀 5分钟快速部署

### 步骤1: 安装依赖包
```bash
cd src/backend/app
pip install -r requirements_canteen.txt
```

这将安装：
- `requests` - HTTP请求库
- `pycryptodome` - AES加密解密
- `selenium` - 浏览器自动化

### 步骤2: 安装浏览器驱动

**选择一个你要使用的浏览器并安装对应驱动：**

#### Chrome (推荐)
1. 下载 [ChromeDriver](https://chromedriver.chromium.org/)
2. 解压到系统PATH目录
3. 验证：`chromedriver --version`

#### Firefox
1. 下载 [GeckoDriver](https://github.com/mozilla/geckodriver/releases)
2. 解压到系统PATH目录
3. 验证：`geckodriver --version`

#### Edge
1. 下载 [EdgeDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
2. 解压到系统PATH目录
3. 验证：`msedgedriver --version`

#### Safari (仅macOS)
1. 打开Safari > 偏好设置 > 高级
2. 勾选"在菜单栏中显示开发菜单"
3. 开发菜单 > 允许远程自动化

### 步骤3: 执行数据库迁移

**Windows:**
```bash
migrate_canteen.bat
```

**Linux/macOS:**
```bash
chmod +x migrate_canteen.sh
./migrate_canteen.sh
```

**或手动执行:**
```bash
python manage.py makemigrations canteen
python manage.py migrate canteen
```

### 步骤4: 启动服务器
```bash
python manage.py runserver
```

## 🎯 快速测试

### 1. 获取JWT令牌（先登录）
```bash
curl -X PATCH http://localhost:8000/api/v1/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

保存返回的JWT令牌。

### 2. 绑定学号
```bash
curl -X POST http://localhost:8000/api/v1/canteen/bind/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "idserial": "2021012345",
    "browser_type": "chrome"
  }'
```

**接下来会发生什么：**
1. 🌐 Chrome浏览器自动打开
2. 🔗 跳转到清华一卡通网站
3. ⏳ 等待你手动登录（最多5分钟）
4. ✅ 登录成功后自动获取cookie
5. 📊 自动爬取并保存消费数据
6. 🔒 浏览器自动关闭

### 3. 查看消费数据
```bash
curl http://localhost:8000/api/v1/canteen/consumption/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

返回示例：
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "idserial": "2021012345",
    "total_amount": "1234.56",
    "canteen_count": 8,
    "canteen_data": {
      "观畴园": 456.78,
      "紫荆园": 345.67,
      "桃李园": 234.56,
      "听涛园": 123.45
    },
    "last_fetched": "2024-11-30T10:30:00Z"
  }
}
```

### 4. 刷新数据（更新最新消费）
```bash
curl -X POST http://localhost:8000/api/v1/canteen/refresh/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "browser_type": "chrome"
  }'
```

## 🎨 前端Vue集成示例

```vue
<template>
  <div class="canteen-consumption">
    <div v-if="!hasBound">
      <h2>绑定学号</h2>
      <input v-model="idserial" placeholder="输入学号" />
      <select v-model="browserType">
        <option value="chrome">Chrome</option>
        <option value="firefox">Firefox</option>
        <option value="edge">Edge</option>
        <option value="safari">Safari</option>
      </select>
      <button @click="bindAccount">绑定</button>
    </div>
    
    <div v-else>
      <h2>消费统计</h2>
      <p>总消费: ¥{{ consumption.total_amount }}</p>
      <p>食堂数量: {{ consumption.canteen_count }}</p>
      
      <h3>各食堂消费</h3>
      <ul>
        <li v-for="(amount, name) in consumption.canteen_data" :key="name">
          {{ name }}: ¥{{ amount }}
        </li>
      </ul>
      
      <button @click="refreshData">刷新数据</button>
      <button @click="unbindAccount">解绑</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      idserial: '',
      browserType: 'chrome',
      consumption: null,
      hasBound: false
    };
  },
  
  async mounted() {
    await this.checkBinding();
  },
  
  methods: {
    async checkBinding() {
      try {
        const response = await fetch('/api/v1/canteen/consumption/', {
          headers: {
            'Authorization': `Bearer ${this.getToken()}`
          }
        });
        
        const result = await response.json();
        if (result.code === 200) {
          this.consumption = result.data;
          this.hasBound = true;
        }
      } catch (error) {
        console.error('检查绑定失败', error);
      }
    },
    
    async bindAccount() {
      this.$message.info('正在打开浏览器，请登录一卡通系统...');
      
      try {
        const response = await fetch('/api/v1/canteen/bind/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.getToken()}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            idserial: this.idserial,
            browser_type: this.browserType
          })
        });
        
        const result = await response.json();
        if (result.code === 200) {
          this.$message.success('绑定成功！');
          this.consumption = { 
            ...result.data, 
            canteen_data: result.data.canteens 
          };
          this.hasBound = true;
        } else {
          this.$message.error(result.message);
        }
      } catch (error) {
        this.$message.error('绑定失败: ' + error.message);
      }
    },
    
    async refreshData() {
      this.$message.info('正在刷新数据...');
      
      try {
        const response = await fetch('/api/v1/canteen/refresh/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.getToken()}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            browser_type: this.browserType
          })
        });
        
        const result = await response.json();
        if (result.code === 200) {
          this.$message.success('刷新成功！');
          await this.checkBinding();
        } else {
          this.$message.error(result.message);
        }
      } catch (error) {
        this.$message.error('刷新失败: ' + error.message);
      }
    },
    
    async unbindAccount() {
      try {
        const response = await fetch('/api/v1/canteen/unbind/', {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${this.getToken()}`
          }
        });
        
        const result = await response.json();
        if (result.code === 200) {
          this.$message.success('解绑成功！');
          this.hasBound = false;
          this.consumption = null;
        }
      } catch (error) {
        this.$message.error('解绑失败: ' + error.message);
      }
    },
    
    getToken() {
      return localStorage.getItem('jwt_token');
    }
  }
};
</script>
```

## 🔧 常见问题解决

### Q1: 提示"未安装selenium"
```bash
pip install selenium
```

### Q2: 浏览器驱动找不到
确保驱动文件在系统PATH中：
- **Windows**: 放到 `C:\Windows\System32\` 或其他PATH目录
- **Linux/macOS**: 放到 `/usr/local/bin/` 或其他PATH目录

### Q3: 登录超时
默认等待时间5分钟，如需调整，修改 `canteen/services.py` 中的 `max_wait_time` 参数。

### Q4: Cookie失效
直接调用刷新接口，系统会自动重新获取。

## 📚 完整文档

- **详细API文档**: `docs/CANTEEN_API.md`
- **功能说明**: `src/backend/app/canteen/README.md`
- **集成总结**: `CANTEEN_INTEGRATION_SUMMARY.md`

## 🎉 完成！

现在你已经成功部署了食堂消费数据功能，可以：
- ✅ 通过API绑定学号
- ✅ 自动爬取消费数据
- ✅ 查看和刷新数据
- ✅ 在前端集成使用

有问题？查看完整文档或提交Issue！
