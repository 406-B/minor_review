#!/bin/bash
set -e

echo "==================================="
echo "Minor Review Backend Starting..."
echo "==================================="

# 等待数据库就绪
echo "Waiting for MySQL..."
while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
  sleep 1
done
echo "MySQL is ready!"

# 如果传入的命令是 pytest，则直接执行该命令（用于集成测试）
if [[ "$1" == "pytest"* ]]; then
    echo "Running tests..."
    exec "$@"
fi

# 安装可能缺失的依赖（临时修复）
echo "Installing additional dependencies..."
pip install requests pycryptodome -q || true

# 运行数据库迁移
echo "Running database migrations..."
python manage.py migrate --noinput

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# 创建媒体文件目录
echo "Creating media directories..."
mkdir -p media/avatars media/dishes

echo "==================================="
echo "Starting Gunicorn server..."
echo "==================================="

# 启动 Gunicorn
exec gunicorn app.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level info
