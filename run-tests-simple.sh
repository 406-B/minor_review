#!/bin/bash
# 简化的测试脚本 - 不依赖db服务

set -e

echo "=========================================="
echo "在 Docker 环境中运行单元测试（简化版）"
echo "=========================================="

# 检查后端镜像是否存在
if ! docker images | grep -q "minor_review-backend"; then
    echo "错误: 后端镜像不存在，请先运行: docker-compose build backend"
    exit 1
fi

# 创建网络（如果不存在）
docker network create minor_review_backend_net 2>/dev/null || true

echo ""
echo "=========================================="
echo "运行后端单元测试"
echo "=========================================="

# 在临时容器中运行后端单元测试
docker run --rm \
    --network minor_review_backend_net \
    -e DJANGO_SETTINGS_MODULE=app.settings_test \
    -v "$(pwd)/src/backend/app:/app" \
    minor_review-backend \
    bash -c "
        cd /app
        pip install -q pytest pytest-django pytest-cov coverage mysqlclient
        pytest --tb=short \"\$@\"
    " -- "$@"

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

