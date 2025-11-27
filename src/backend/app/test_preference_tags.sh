#!/bin/bash

# 用户偏好标签功能测试脚本
# 使用方法：./test_preference_tags.sh <your_token>

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务器地址
BASE_URL="http://localhost:8000/api"

# 检查 token 参数
if [ -z "$1" ]; then
    echo -e "${RED}错误：请提供认证 token${NC}"
    echo "使用方法：$0 <your_token>"
    exit 1
fi

TOKEN=$1

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}用户偏好标签功能测试${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 测试 1: 获取所有可用标签
echo -e "${YELLOW}测试 1: 获取所有可用标签${NC}"
echo "GET $BASE_URL/list/tags/"
curl -s -X GET "$BASE_URL/list/tags/" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# 测试 2: 获取用户当前偏好标签（可能为空）
echo -e "${YELLOW}测试 2: 获取用户当前偏好标签${NC}"
echo "GET $BASE_URL/profile/preference-tags"
curl -s -X GET "$BASE_URL/profile/preference-tags" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# 测试 3: 设置用户偏好标签（覆盖模式）
echo -e "${YELLOW}测试 3: 设置用户偏好标签（覆盖模式）${NC}"
echo "POST $BASE_URL/profile/preference-tags/set"
echo "请求体：{ \"tag_ids\": [1, 2, 3] }"
curl -s -X POST "$BASE_URL/profile/preference-tags/set" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag_ids": [1, 2, 3]}' | jq '.'
echo ""
echo ""

# 测试 4: 再次获取用户偏好标签（应该有数据了）
echo -e "${YELLOW}测试 4: 再次获取用户偏好标签${NC}"
echo "GET $BASE_URL/profile/preference-tags"
curl -s -X GET "$BASE_URL/profile/preference-tags" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# 测试 5: 添加新的偏好标签（追加模式）
echo -e "${YELLOW}测试 5: 添加新的偏好标签（追加模式）${NC}"
echo "POST $BASE_URL/profile/preference-tags/add"
echo "请求体：{ \"tag_ids\": [4, 5] }"
curl -s -X POST "$BASE_URL/profile/preference-tags/add" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tag_ids": [4, 5]}' | jq '.'
echo ""
echo ""

# 测试 6: 获取个性化推荐菜品
echo -e "${YELLOW}测试 6: 获取个性化推荐菜品（第1页，每页10条）${NC}"
echo "GET $BASE_URL/profile/recommended-dishes?page=1&page_size=10"
curl -s -X GET "$BASE_URL/profile/recommended-dishes?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

# 测试 7: 获取用户个人资料（包含偏好标签）
echo -e "${YELLOW}测试 7: 获取用户个人资料（包含偏好标签）${NC}"
echo "GET $BASE_URL/profile/profile"
curl -s -X GET "$BASE_URL/profile/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}测试完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}注意事项：${NC}"
echo "1. 请确保数据库中有标签数据（至少ID为1-5的标签存在）"
echo "2. 如果返回 404，说明用户未设置偏好标签"
echo "3. 如果返回 401，说明 token 无效或已过期"
echo "4. 使用 jq 命令格式化 JSON 输出，如果没有安装 jq，请移除脚本中的 '| jq .''"

