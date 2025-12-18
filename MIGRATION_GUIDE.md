# SQLite 到 MySQL 数据迁移指南

## 方法一：使用迁移脚本（推荐）

### 步骤1：准备环境

1. 安装必要的Python包：
```bash
pip install mysql-connector-python
```

2. 修改 `docker-compose.yaml`，暴露MySQL端口：
```yaml
db:
  image: mysql:8.0
  ports:
    - "3306:3306"  # 添加这一行
  # ... 其他配置
```

3. 重启数据库容器：
```bash
docker-compose restart db
```

### 步骤2：执行迁移

1. 将SQLite数据库文件（`db.sqlite3`）放在项目根目录

2. 运行迁移脚本：
```bash
python migrate_sqlite_to_mysql.py
```

3. 按提示操作，输入 `yes` 确认迁移

## 方法二：使用Django的dumpdata和loaddata

### 步骤1：从SQLite导出数据

```bash
# 进入Django项目目录
cd src/backend/app

# 导出所有数据（排除contenttypes和auth.permission）
python manage.py dumpdata \
  --exclude contenttypes \
  --exclude auth.permission \
  --indent 2 \
  --output data_backup.json
```

### 步骤2：切换到MySQL并导入

1. 修改 `settings.py` 或设置环境变量使用MySQL

2. 运行迁移创建表结构：
```bash
python manage.py migrate
```

3. 导入数据：
```bash
python manage.py loaddata data_backup.json
```

## 方法三：使用第三方工具

### 使用 sqlite3-to-mysql

```bash
# 安装工具
pip install sqlite3-to-mysql

# 执行迁移
sqlite3mysql -f db.sqlite3 \
  -d minor_review \
  -u root \
  -p database \
  --mysql-host localhost
```

## 访问MySQL数据库

### 1. 使用命令行

```bash
# Docker环境
docker exec -it minor_review_db mysql -u root -pdatabase minor_review

# 本地环境
mysql -u root -p minor_review
```

### 2. 使用图形化工具

推荐工具：
- **MySQL Workbench** (官方工具)
- **DBeaver** (跨平台，支持多种数据库)
- **phpMyAdmin** (Web界面)
- **HeidiSQL** (Windows)
- **Sequel Pro** (macOS)

连接配置：
- 主机: `localhost`
- 端口: `3306`
- 用户名: `root`
- 密码: `database`
- 数据库: `minor_review`

### 3. 使用Python代码

```python
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='database',
    database='minor_review'
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM your_table LIMIT 10")
for row in cursor.fetchall():
    print(row)

conn.close()
```

## 常见问题

### Q1: 迁移后主键冲突怎么办？

清空MySQL数据后重新迁移：
```sql
-- 在MySQL中执行
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE table_name;
SET FOREIGN_KEY_CHECKS = 1;
```

### Q2: 字符编码问题

确保使用UTF-8编码：
```python
# 在迁移脚本中设置
MYSQL_CONFIG = {
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'use_unicode': True
}
```

### Q3: 日期时间格式问题

SQLite和MySQL的日期时间格式可能不同，需要转换：
```python
from datetime import datetime

# 转换日期格式
if isinstance(value, str):
    try:
        dt = datetime.fromisoformat(value)
        value = dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
```

### Q4: 如何验证迁移是否成功？

```sql
-- 检查表数量
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'minor_review';

-- 检查各表记录数
SELECT table_name, table_rows 
FROM information_schema.tables 
WHERE table_schema = 'minor_review';
```

## 注意事项

1. **备份数据**：迁移前务必备份原始SQLite文件
2. **测试环境**：先在测试环境测试迁移过程
3. **权限问题**：确保MySQL用户有足够权限
4. **数据类型**：某些SQLite类型可能需要手动调整
5. **外键约束**：迁移时可能需要暂时禁用外键检查
