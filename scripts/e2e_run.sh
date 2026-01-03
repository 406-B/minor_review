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
dos2unix src/backend/entrypoint.sh
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

# 导入 cypress/fixtures 下的 Django fixtures（如果存在）
echo "Importing Django fixtures from cypress/fixtures if present..."
if [ -d "cypress/fixtures" ]; then
  echo "Copying fixtures into backend container..."
  # 将主机上的 fixtures 目录复制到后端容器的 /app/fixtures
  sudo docker cp cypress/fixtures/. minor_review_backend_e2e:/app/fixtures || true

  # Load fixtures sequentially (explicit checks). 输出 ✅ 在每个成功加载后。
  echo "Loading fixtures sequentially..."

  if [ -f "cypress/fixtures/users.json" ]; then
    echo "Processing users fixture (will encrypt passwords and upsert into login.User): users.json"
    sudo docker compose $COMPOSE_FILES exec -T backend python manage.py shell <<'PY'
import json, os
from login.models import User
from utils.jwt import encrypt_password
fpath = '/app/fixtures/users.json'
if os.path.exists(fpath):
    with open(fpath, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    for item in data:
        fields = item.get('fields', {})
        username = fields.get('username')
        raw_pw = fields.get('password')
        nickname = fields.get('nickname', '')
        avatar = fields.get('avatar', None)
        if not username or raw_pw is None:
            continue
        enc = encrypt_password(raw_pw)
        obj, created = User.objects.update_or_create(username=username, defaults={'password': enc, 'nickname': nickname})
        if avatar:
            try:
                obj.avatar = avatar
                obj.save()
            except Exception:
                pass
    print('Users processed')
else:
    print('No users.json found at', fpath)
PY
    echo "✅ users.json processed"
  fi

  if [ -f "cypress/fixtures/canteen.json" ]; then
    # Ensure floors/windows exist before loading dishes inside canteen.json
    if [ -f "cypress/fixtures/floors.json" ]; then
      echo "Loading fixture: floors.json"
      if sudo docker compose $COMPOSE_FILES exec -T backend python manage.py loaddata "/app/fixtures/floors.json"; then
        echo "✅ floors.json loaded"
      else
        echo "Warning: failed to load fixture floors.json"
      fi
    fi

    if [ -f "cypress/fixtures/windows.json" ]; then
      echo "Loading fixture: windows.json"
      if sudo docker compose $COMPOSE_FILES exec -T backend python manage.py loaddata "/app/fixtures/windows.json"; then
        echo "✅ windows.json loaded"
      else
        echo "Warning: failed to load fixture windows.json"
      fi
    fi

    echo "Loading fixture: canteen.json"
    if sudo docker compose $COMPOSE_FILES exec -T backend python manage.py loaddata "/app/fixtures/canteen.json"; then
      echo "✅ canteen.json loaded"
    else
      echo "Warning: failed to load fixture canteen.json"
    fi
  fi

  if [ -f "cypress/fixtures/posts.json" ]; then
    echo "Loading fixture: posts.json"
    if sudo docker compose $COMPOSE_FILES exec -T backend python manage.py loaddata "/app/fixtures/posts.json"; then
      echo "✅ posts.json loaded"
    else
      echo "Warning: failed to load fixture posts.json"
    fi
  fi

  if [ -f "cypress/fixtures/comments.json" ]; then
    echo "Loading fixture: comments.json"
    if sudo docker compose $COMPOSE_FILES exec -T backend python manage.py loaddata "/app/fixtures/comments.json"; then
      echo "✅ comments.json loaded"
    else
      echo "Warning: failed to load fixture comments.json"
    fi
  fi

  if [ -f "cypress/fixtures/profile.json" ]; then
    echo "Loading fixture: profile.json"
    if sudo docker compose $COMPOSE_FILES exec -T backend python manage.py loaddata "/app/fixtures/profile.json"; then
      echo "✅ profile.json loaded"
    else
      echo "Warning: failed to load fixture profile.json"
    fi
  fi

  # Load any remaining fixture files not explicitly handled
  for f in cypress/fixtures/*.json cypress/fixtures/*.yaml cypress/fixtures/*.yml; do
    if [ -f "$f" ]; then
      fname=$(basename "$f")
      case "$fname" in
        users.json|canteen.json|posts.json|comments.json|profile.json|floors.json|windows.json)
          ;;
        *)
          echo "Loading fixture: $fname"
          if sudo docker compose $COMPOSE_FILES exec -T backend python manage.py loaddata "/app/fixtures/$fname"; then
            echo "✅ $fname loaded"
          else
            echo "Warning: failed to load fixture $fname"
          fi
          ;;
      esac
    fi
  done
else
  echo "No cypress/fixtures directory found; skipping fixture import."
fi

echo ""
echo "=========================================="
echo "✅ E2E 测试环境部署完成！"
echo "=========================================="
