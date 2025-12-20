-- E2E 测试数据库初始化脚本
CREATE DATABASE IF NOT EXISTS minor_review_e2e CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE minor_review_e2e;

-- 设置时区
SET time_zone = '+08:00';

-- 创建初始表（可选，Django 会自动创建）
-- Django migrations 会处理所有表的创建
