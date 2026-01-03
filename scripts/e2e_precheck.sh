#!/usr/bin/env bash
set -euo pipefail

# 检查并清理可能冲突的 E2E 容器
echo "=========================================="
echo "Checking for conflicting containers..."
echo "=========================================="

# 停止并删除任何残留的 E2E 容器
echo "Stopping any existing E2E containers..."
sudo docker stop minor_review_db_e2e 2>/dev/null || true
sudo docker stop minor_review_redis_e2e 2>/dev/null || true
sudo docker stop minor_review_backend_e2e 2>/dev/null || true
sudo docker stop minor_review_frontend_e2e 2>/dev/null || true
sudo docker stop minor_review_nginx_e2e 2>/dev/null || true
sudo docker stop minor_review_cypress_e2e 2>/dev/null || true

echo "Removing any existing E2E containers..."
sudo docker rm minor_review_db_e2e 2>/dev/null || true
sudo docker rm minor_review_redis_e2e 2>/dev/null || true
sudo docker rm minor_review_backend_e2e 2>/dev/null || true
sudo docker rm minor_review_frontend_e2e 2>/dev/null || true
sudo docker rm minor_review_nginx_e2e 2>/dev/null || true
sudo docker rm minor_review_cypress_e2e 2>/dev/null || true

echo ""
echo "Checking port availability..."
# 检查端口是否被占用
if netstat -tuln 2>/dev/null | grep -q ":33307 " || ss -tuln 2>/dev/null | grep -q ":33307 "; then
    echo "⚠️  Warning: Port 33307 is in use"
    netstat -tuln 2>/dev/null | grep ":33307" || ss -tuln 2>/dev/null | grep ":33307"
else
    echo "✅ Port 33307 is available"
fi

if netstat -tuln 2>/dev/null | grep -q ":8081 " || ss -tuln 2>/dev/null | grep -q ":8081 "; then
    echo "⚠️  Warning: Port 8081 is in use"
    netstat -tuln 2>/dev/null | grep ":8081" || ss -tuln 2>/dev/null | grep ":8081"
else
    echo "✅ Port 8081 is available"
fi

echo ""
echo "=========================================="
echo "Pre-check completed!"
echo "=========================================="
