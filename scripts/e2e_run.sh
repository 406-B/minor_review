#!/usr/bin/env bash
set -euo pipefail

# 启动选项说明：
# - 本脚本基于项目根的 docker-compose.yaml 与 docker-compose.e2e.yaml
# - 在服务器上运行时，会：
#   1) 启动 db/redis/backend/frontend/nginx（可按需修改服务列表）
#   2) 等待后端健康检查通过
#   3) 运行 Django 迁移与可选的 fixtures 加载
#   4) 运行 Cypress 容器执行 E2E 测试

export COMPOSE_PROJECT_NAME=minor_review_e2e
COMPOSE_FILES="-f docker-compose.e2e.yaml"

echo "=========================================="
echo "Starting E2E Test Environment"
echo "=========================================="

# 预检查：清理可能的冲突
echo "Running pre-check and cleanup..."
bash "$(dirname "$0")/e2e_precheck.sh" || true

echo ""
echo "Building and bringing up services..."
sudo docker compose $COMPOSE_FILES up -d --build db redis backend frontend nginx

echo "Waiting for backend health endpoint..."
MAX_WAIT=120
WAITED=0
until sudo docker compose $COMPOSE_FILES exec -T backend sh -c "curl -sSf http://localhost:8000/api/v1/health/ >/dev/null 2>&1"; do
  sleep 2
  WAITED=$((WAITED+2))
  echo "  waiting... ${WAITED}s"
  if [ $WAITED -ge $MAX_WAIT ]; then
    echo "Backend health check failed after ${MAX_WAIT}s"
    sudo docker compose $COMPOSE_FILES ps
    sudo docker compose $COMPOSE_FILES logs backend --no-color | tail -n 200
    exit 1
  fi
done

echo "Running migrations..."
sudo docker compose $COMPOSE_FILES exec -T backend python manage.py makemigrations --noinput || true
sudo docker compose $COMPOSE_FILES exec -T backend python manage.py migrate --noinput

echo "Ensuring test user exists..."
sudo docker compose $COMPOSE_FILES exec -T backend python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.filter(username='tester123').exists() or User.objects.create_user('tester123','tester123@example.com','123456Aa-')"

echo "Creating other test users..."
sudo docker compose $COMPOSE_FILES exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
# Create alice (id=1)
if not User.objects.filter(username='alice').exists():
    User.objects.create_user('alice', 'alice@example.com', 'password123')
    print('Created user: alice')
# Create bob (id=2)
if not User.objects.filter(username='bob').exists():
    User.objects.create_user('bob', 'bob@example.com', 'password123')
    print('Created user: bob')
# Create charlie (id=3)
if not User.objects.filter(username='charlie').exists():
    User.objects.create_user('charlie', 'charlie@example.com', 'password123')
    print('Created user: charlie')
print('All test users ready')
" || true

echo "Initializing test data..."
# 运行数据初始化脚本（如果存在）
if [ -f "src/backend/app/data_filing/populate_database.py" ]; then
  echo "Running populate_database.py..."
  sudo docker compose $COMPOSE_FILES exec -T backend python data_filing/populate_database.py || true
fi

echo ""
echo "Note: Cypress fixtures (cypress/fixtures/*.json) are used by Cypress tests directly"
echo "      and do not need to be loaded into Django database."
echo ""

echo "Running Cypress tests in docker..."
sudo docker compose $COMPOSE_FILES run --rm cypress
CYPRESS_EXIT_CODE=$?

echo "=========================================="
echo "Collecting test artifacts..."
echo "=========================================="
# artifacts (videos/screenshots) are mounted into the repo by the cypress service
echo "Test videos: ./cypress/videos"
echo "Screenshots: ./cypress/screenshots"

if [ $CYPRESS_EXIT_CODE -ne 0 ]; then
  echo ""
  echo "=========================================="
  echo "⚠️  Cypress tests failed with exit code: $CYPRESS_EXIT_CODE"
  echo "=========================================="
  exit $CYPRESS_EXIT_CODE
fi

echo ""
echo "=========================================="
echo "✅ E2E tests completed successfully!"
echo "=========================================="
