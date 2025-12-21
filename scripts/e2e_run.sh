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

echo ""
echo "Note: Test users created. E2E tests will create their own data during execution."
echo "      (populate_database.py is not needed for E2E tests)"
echo ""

echo "Running Cypress tests in docker..."
echo "=========================================="
sudo docker compose -f docker-compose.e2e.yaml run --rm --entrypoint "/bin/sh" cypress -c "npx cypress run --reporter spec"
CYPRESS_EXIT_CODE=$?

echo ""
echo "=========================================="
echo "📊 Test Results Summary"
echo "=========================================="

# 解析测试结果
if [ -f cypress_output.log ]; then
  # 提取测试统计
  PASSING=$(grep -oP '✔\s+\K\d+(?=\s+passing)' cypress_output.log | tail -1 || echo "0")
  FAILING=$(grep -oP '\d+(?=\s+failing)' cypress_output.log | tail -1 || echo "0")
  PENDING=$(grep -oP '\d+(?=\s+pending)' cypress_output.log | tail -1 || echo "0")
  
  echo "Tests Passed:  ${PASSING}"
  echo "Tests Failed:  ${FAILING}"
  [ "$PENDING" != "0" ] && echo "Tests Pending: ${PENDING}"
  
  # 显示失败的测试
  if [ "$FAILING" != "0" ]; then
    echo ""
    echo "❌ Failed Tests:"
    grep -A 2 "failing)" cypress_output.log | tail -20 || true
  fi
  
  rm -f cypress_output.log
fi

echo ""
echo "Test artifacts location:"
echo "  - Videos:      ./cypress/videos"
echo "  - Screenshots: ./cypress/screenshots"

if [ $CYPRESS_EXIT_CODE -ne 0 ]; then
  echo ""
  echo "=========================================="
  echo "⚠️  E2E tests FAILED (exit code: $CYPRESS_EXIT_CODE)"
  echo "=========================================="
  echo ""
  echo "Check the videos and screenshots above for details."
  exit $CYPRESS_EXIT_CODE
fi

echo ""
echo "=========================================="
echo "✅ All E2E tests PASSED!"
echo "=========================================="
