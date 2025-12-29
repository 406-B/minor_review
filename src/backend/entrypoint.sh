#!/bin/bash
set -e

echo "==================================="
echo "Minor Review Backend Starting..."
echo "==================================="

# 绛夊緟鏁版嵁搴撳氨缁?
echo "Waiting for MySQL..."
while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
  sleep 1
done
echo "MySQL is ready!"

# 瀹夎鍙兘缂哄け鐨勪緷璧栵紙涓存椂淇锛?
echo "Installing additional dependencies..."
pip install requests pycryptodome -q || true

# 杩愯鏁版嵁搴撹縼绉?
echo "Running database migrations..."
python manage.py migrate --noinput

# 鏀堕泦闈欐€佹枃浠?
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# 鍒涘缓濯掍綋鏂囦欢鐩綍
echo "Creating media directories..."
mkdir -p media/avatars media/dishes

echo "==================================="
echo "Starting Gunicorn server..."
echo "==================================="

# 鍚姩 Gunicorn
exec gunicorn app.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level info
