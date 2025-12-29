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

# 等待Redis就绪
echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done
echo "Redis is ready!"

# 安装/更新依赖（确保新依赖已安装）
echo "Installing/Updating dependencies..."
pip install --no-cache-dir -r requirements.txt -q

# 检查并合并迁移冲突
echo "Checking for migration conflicts..."
python manage.py makemigrations --merge --noinput 2>/dev/null || echo "No conflicts to merge"

# 运行数据库迁移
echo "Running database migrations..."
python manage.py migrate --noinput

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# 创建媒体文件目录
echo "Creating media directories..."
mkdir -p media/avatars media/dishes

# 验证Redis缓存连接
echo "Verifying Redis cache connection..."
if [ -n "$REDIS_PASSWORD" ]; then
    python manage.py shell -c "from django.core.cache import cache; cache.set('test', 'ok'); print('✅ Redis cache with auth OK' if cache.get('test') == 'ok' else '❌ Redis cache failed')" || echo "⚠️  Cache check skipped"
else
    python manage.py shell -c "from django.core.cache import cache; cache.set('test', 'ok'); print('✅ Redis cache OK' if cache.get('test') == 'ok' else '❌ Redis cache failed')" || echo "⚠️  Cache check skipped"
fi

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

