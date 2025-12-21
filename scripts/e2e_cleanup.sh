#!/usr/bin/env bash
set -euo pipefail

# 清理 E2E 运行产生的容器和网络
export COMPOSE_PROJECT_NAME=minor_review_e2e
COMPOSE_FILES="-f docker-compose.e2e.yaml"

echo "=========================================="
echo "Cleaning up E2E environment..."
echo "=========================================="

echo "Stopping and removing containers..."
sudo docker compose $COMPOSE_FILES down

echo ""
echo "E2E containers and networks have been removed."
echo ""
echo "To remove E2E volumes (test database and data), run:"
echo "  sudo docker volume rm minor_review_mysql_data_e2e"
echo "  sudo docker volume rm minor_review_redis_data_e2e"
echo "  sudo docker volume rm minor_review_media_e2e"
echo "  sudo docker volume rm minor_review_static_e2e"
echo ""
echo "Or remove all E2E volumes at once:"
echo "  sudo docker volume rm \$(sudo docker volume ls -q | grep '_e2e')"
