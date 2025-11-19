-- 本地开发环境 MySQL 数据库初始化脚本
-- 使用方式: mysql -u root -p < init_local_db.sql

-- 创建数据库
CREATE DATABASE IF NOT EXISTS minor_review 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 授予权限（如果需要）
GRANT ALL PRIVILEGES ON minor_review.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

USE minor_review;

-- 数据库已准备就绪，请运行 Django 迁移命令：
-- python manage.py makemigrations
-- python manage.py migrate
