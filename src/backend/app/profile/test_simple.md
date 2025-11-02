# 部署前检查清单

在部署用户个人资料功能前，请确保完成以下所有步骤：

## ✅ 后端部署检查

### 1. 依赖安装
- [ ] 安装Pillow库：`pip install Pillow`
- [ ] 验证安装：`python -c "import PIL; print(PIL.__version__)"`

### 2. 数据库迁移
- [ ] 生成迁移文件：`python manage.py makemigrations`
- [ ] 检查迁移文件内容（应该包含添加avatar字段）
- [ ] 执行迁移：`python manage.py migrate`
- [ ] 验证迁移：`python manage.py showmigrations login`

### 3. 媒体文件配置
- [ ] 确认 `settings.py` 中配置了 `MEDIA_URL` 和 `MEDIA_ROOT`
- [ ] 确认 `urls.py` 中添加了media文件路由
- [ ] 创建media目录：`src/backend/app/media/avatars/`
- [ ] 添加默认头像文件：`media/avatars/default.png`

### 4. 代码验证
- [ ] 检查 `login/models.py` 中avatar字段已添加
- [ ] 检查 `login/serializers.py` 文件存在且正确
- [ ] 检查 `login/views.py` 中新增了3个视图函数
- [ ] 检查 `login/controllers.py` 中新增了2个控制器函数
- [ ] 检查 `login/urls.py` 中新增了3个路由

### 5. 服务器启动
- [ ] 启动开发服务器：`python manage.py runserver`
- [ ] 检查控制台无错误输出
- [ ] 访问 http://localhost:8000/admin 确认服务正常

## ✅ API测试检查

### 1. 基础功能测试

#### 注册测试
```bash
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","nickname":"Test"}'

curl -X POST http://localhost:8000/api/v1/register -H "Content-Type: application/json" -d "{\"username\":\"testuser1\",\"password\":\"75312552159Aa_\",\"nickname\":\"Test\"}"
```
- [ ] 返回200状态码
- [ ] 数据库中创建了新用户
- [ ] 用户有默认头像字段

#### 登录测试
```bash
curl -X PATCH http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

curl -X PATCH http://localhost:8000/api/v1/login -H "Content-Type: application/json" -d "{\"username\":\"testuser1\",\"password\":\"75312552159Aa_\"}"
```
- [ ] 返回200状态码
- [ ] 返回有效的JWT Token
- [ ] Token包含用户信息

### 2. 个人资料功能测试

#### 获取个人资料
```bash
curl -X GET http://localhost:8000/api/v1/profile \
  -H "Authorization: YOUR_JWT_TOKEN"

curl -X GET http://localhost:8000/api/v1/profile -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
- [ ] 返回200状态码
- [ ] 返回完整的用户信息（id, username, nickname, avatar, created, updated）
- [ ] avatar字段是完整的URL

#### 更新昵称
```bash
curl -X PUT http://localhost:8000/api/v1/profile/update \
  -H "Authorization: YOUR_JWT_TOKEN" \
  -F "nickname=New Nickname"

curl -X PUT http://localhost:8000/api/v1/profile/update -H "Authorization: Bearer YOUR_JWT_TOKEN" -F "nickname=New Nickname"
```
- [ ] 返回200状态码
- [ ] 数据库中昵称已更新
- [ ] updated时间已更新

#### 更新头像
```bash
curl -X PUT http://localhost:8000/api/v1/profile/update \
  -H "Authorization: YOUR_JWT_TOKEN" \
  -F "avatar=@test.png"
```
- [ ] 返回200状态码
- [ ] 图片文件已保存到media/avatars/
- [ ] 返回新的头像URL
- [ ] 可以通过URL访问头像

#### 修改密码
```bash
curl -X POST http://localhost:8000/api/v1/profile/password \
  -H "Authorization: YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"test123","new_password":"newpass","confirm_password":"newpass"}'

curl -X POST http://localhost:8000/api/v1/profile/password -H "Authorization: Bearer YOUR_JWT_TOKEN" -H "Content-Type: application/json" -d "{\"old_password\":\"75312552159Aa_\",\"new_password\":\"NewSecurePass123!\",\"confirm_password\":\"NewSecurePass123!\"}"
```
- [ ] 返回200状态码
- [ ] 可以用新密码登录
- [ ] 旧密码无法登录

### 3. 错误处理测试

#### 未登录访问
```bash
curl -X GET http://localhost:8000/api/v1/profile
```
- [ ] 返回401状态码

#### 旧密码错误
- [ ] 修改密码时提供错误的旧密码，返回400

#### 新密码不一致
- [ ] new_password和confirm_password不同，返回400

#### 无效的图片文件
- [ ] 上传非图片文件，应该有适当的错误处理

## ✅ 文档检查

### API文档
- [ ] `docs/api/openapi.json` 已更新
- [ ] `docs/api/USER_PROFILE_API.md` 存在且完整
- [ ] `docs/api/QUICKSTART.md` 存在且完整
- [ ] `docs/api/README.md` 已更新索引
- [ ] `docs/api/frontend-integration-example.js` 提供前端示例

### 项目文档
- [ ] `IMPLEMENTATION_SUMMARY.md` 总结了所有变更
- [ ] `src/backend/app/MIGRATION_NOTES.md` 说明数据库迁移
- [ ] `src/backend/app/media/avatars/README.md` 说明头像目录

## ✅ Apifox集成检查

### 导入测试
- [ ] 在Apifox中导入 `docs/api/openapi.json`
- [ ] 所有API端点都正确导入
- [ ] 请求/响应schema正确
- [ ] 认证配置正确（Bearer Token）

### 功能测试
- [ ] 在Apifox中测试所有端点
- [ ] 所有测试用例通过
- [ ] 错误情况返回正确的错误码和消息

## ✅ 前端对接检查

### 文档提供
- [ ] 向前端团队提供 `USER_PROFILE_API.md`
- [ ] 向前端团队提供 `frontend-integration-example.js`
- [ ] 向前端团队提供测试用的JWT Token

### 对接指导
- [ ] 说明所有端点需要JWT认证
- [ ] 说明头像上传使用multipart/form-data
- [ ] 说明错误处理方式
- [ ] 提供测试环境URL

## ✅ 安全检查

### 认证与授权
- [ ] 所有个人资料API需要JWT认证
- [ ] 用户只能访问和修改自己的资料
- [ ] Token过期后正确返回401

### 数据验证
- [ ] 昵称不能为空
- [ ] 新密码最少6位
- [ ] 两次新密码必须一致
- [ ] 旧密码验证正确

### 文件上传安全
- [ ] 验证文件类型
- [ ] 限制文件大小
- [ ] 安全的文件名处理

## ✅ 性能检查

### 数据库
- [ ] avatar字段有默认值，不会NULL
- [ ] 图片文件名避免冲突
- [ ] 数据库查询效率正常

### 文件存储
- [ ] media目录有足够空间
- [ ] 文件读写权限正确
- [ ] 考虑定期清理未使用的头像文件

## ✅ 生产环境准备

### 配置调整
- [ ] 修改 `ALLOWED_HOSTS`
- [ ] 设置正确的 `MEDIA_ROOT` 和 `MEDIA_URL`
- [ ] 配置静态文件服务（nginx等）
- [ ] 关闭 `DEBUG` 模式

### 备份
- [ ] 备份数据库
- [ ] 备份media文件
- [ ] 准备回滚方案

## 📝 完成记录

完成日期：__________
测试人员：__________
部署人员：__________

## 🐛 已知问题

记录任何已知问题或限制：

1. 
2. 
3. 

## 📞 支持联系

如有问题，请联系：
- 后端负责人：__________
- 技术支持：__________
