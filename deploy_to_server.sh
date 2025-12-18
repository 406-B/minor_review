#!/bin/bash
# Minor Review 项目服务器部署脚本
# 直接在服务器上部署，跳过本地 Docker 构建问题

set -e

echo "==================================="
echo "Minor Review 项目服务器部署"
echo "==================================="

# 检查是否在服务器环境
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装 Docker，请先安装 Docker"
    exit 1
fi

# 获取项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "项目目录: $PROJECT_DIR"

# 步骤 1: 清理可能存在的旧容器
echo ""
echo "步骤 1: 清理旧容器..."
docker-compose down -v 2>/dev/null || true
docker system prune -f

# 步骤 2: 配置 Docker 镜像源（如果在中国大陆服务器）
echo ""
echo "步骤 2: 配置 Docker 镜像源..."
if curl -s --connect-timeout 3 registry.docker-cn.com > /dev/null 2>&1; then
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://registry.docker-cn.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF
    systemctl restart docker 2>/dev/null || service docker restart 2>/dev/null || true
    echo "✓ 已配置 Docker 镜像源"
else
    echo "✓ 使用 Docker Hub 官方源"
fi

# 步骤 3: 拉取镜像
echo ""
echo "步骤 3: 拉取 Docker 镜像..."
docker pull mysql:8.1
docker pull nginx:latest
docker pull phpmyadmin/phpmyadmin:latest

# 步骤 4: 构建应用镜像
echo ""
echo "步骤 4: 构建应用镜像..."
docker build -t minor-review-backend ./src/backend
docker build -t minor-review-frontend ./src/frontend

# 步骤 5: 启动服务
echo ""
echo "步骤 5: 启动服务..."
docker-compose up -d

# 步骤 6: 等待数据库就绪
echo ""
echo "步骤 6: 等待数据库就绪..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T db mysqladmin ping -h localhost -u root -pdatabase --silent 2>/dev/null; then
        echo "✓ 数据库已就绪"
        break
    fi
    attempt=$((attempt + 1))
    echo "等待数据库启动... ($attempt/$max_attempts)"
    sleep 3
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ 数据库启动超时"
    exit 1
fi

# 步骤 7: 执行数据库迁移
echo ""
echo "步骤 7: 执行数据库迁移..."
docker-compose exec -T backend python manage.py migrate --noinput

# 步骤 8: 收集静态文件
echo ""
echo "步骤 8: 收集静态文件..."
docker-compose exec -T backend python manage.py collectstatic --noinput --clear

# 步骤 9: 重启服务确保配置生效
echo ""
echo "步骤 9: 重启服务..."
docker-compose restart

echo ""
echo "==================================="
echo "✓ 部署完成！"
echo "==================================="
echo ""
echo "服务状态:"
docker-compose ps

echo ""
echo "访问地址:"
echo "  - 前端: http://your-server-ip"
echo "  - 后端 API: http://your-server-ip/api/v1/"
echo "  - phpMyAdmin: http://your-server-ip:8080"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  重启服务: docker-compose restart"
echo "  停止服务: docker-compose down"
echo ""
echo "数据迁移:"
echo "  如需迁移 SQLite 数据，请手动执行:"
echo "  python migrate_sqlite_to_mysql.py"

echo ""
echo "==================================="

