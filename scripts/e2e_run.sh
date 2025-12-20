#!/usr/bin/env bash
set -euo pipefail

# 启动选项说明：
# - 本脚本基于项目根的 docker-compose.yaml 与 docker-compose.e2e.yaml
# - 在服务器上运行时，会：
#   1) 启动 db/backend/frontend/nginx（可按需修改服务列表）
#   2) 等待后端健康检查通过
#   3) 运行 Django 迁移与可选的 fixtures 加载
#   4) 运行 Cypress 容器执行 E2E 测试

export COMPOSE_PROJECT_NAME=minor_review_e2e
COMPOSE_FILES="-f docker-compose.yaml -f docker-compose.e2e.yaml"

echo "Bringing up DB, backend, frontend and nginx..."
docker-compose $COMPOSE_FILES up -d db backend frontend nginx

echo "Waiting for backend health endpoint..."
MAX_WAIT=120
WAITED=0
until docker-compose $COMPOSE_FILES exec -T backend sh -c "curl -sSf http://localhost:8000/api/v1/health/ >/dev/null 2>&1"; do
  sleep 2
  WAITED=$((WAITED+2))
  echo "  waiting... ${WAITED}s"
  if [ $WAITED -ge $MAX_WAIT ]; then
    echo "Backend health check failed after ${MAX_WAIT}s"
    docker-compose $COMPOSE_FILES ps
    docker-compose $COMPOSE_FILES logs backend --no-color | tail -n 200
    exit 1
  fi
done

echo "Running migrations..."
docker-compose $COMPOSE_FILES exec -T backend python manage.py makemigrations --noinput || true
docker-compose $COMPOSE_FILES exec -T backend python manage.py migrate --noinput

# 可选：加载 fixtures（如果你放置了 fixtures 文件）
if [ -d "cypress/fixtures" ]; then
  echo "Loading fixtures (if any)..."
  # 尝试加载常见 fixtures 文件
  for f in cypress/fixtures/*.json; do
    [ -e "$f" ] || continue
    filename=$(basename "$f")
    echo "  loaddata $filename"
    docker-compose $COMPOSE_FILES exec -T backend python manage.py loaddata "cypress/fixtures/$filename" || true
  done
fi

echo "Running Cypress tests in docker..."
docker-compose $COMPOSE_FILES run --rm cypress || RC=$?

echo "Cypress finished. Collecting artifacts..."
# artifacts (videos/screenshots) are mounted into the repo by the cypress service
echo "Artifacts location: ./cypress/videos and ./cypress/screenshots"

if [ -n "${RC-}" ]; then
  echo "Cypress exited with code ${RC}" >&2
  exit ${RC}
fi

echo "E2E run complete."
