#!/usr/bin/env bash
set -euo pipefail

# 清理 E2E 运行产生的容器和网络
export COMPOSE_PROJECT_NAME=minor_review_e2e
COMPOSE_FILES="-f docker-compose.yaml -f docker-compose.e2e.yaml"

echo "Stopping and removing containers..."
docker-compose $COMPOSE_FILES down

echo "You can remove volumes manually if desired. Example:"
echo "  docker volume rm minor_review_mysql_data minor_review_media minor_review_static"
