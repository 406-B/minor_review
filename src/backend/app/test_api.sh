#!/bin/bash
# API 测试脚本

echo "========================================="
echo "测试食堂列表 API"
echo "========================================="
curl -X GET "http://127.0.0.1:8000/api/canteens/" \
  -H "Accept: application/json"

echo -e "\n\n========================================="
echo "测试标签列表 API"
echo "========================================="
curl -X GET "http://127.0.0.1:8000/api/tags/" \
  -H "Accept: application/json"

echo -e "\n\n========================================="
echo "测试菜品列表 API"
echo "========================================="
curl -X GET "http://127.0.0.1:8000/api/dishes/" \
  -H "Accept: application/json"

echo -e "\n\n========================================="
echo "测试热门菜品 API"
echo "========================================="
curl -X GET "http://127.0.0.1:8000/api/dishes/hot/?limit=5" \
  -H "Accept: application/json"

echo -e "\n\n测试完成！"

