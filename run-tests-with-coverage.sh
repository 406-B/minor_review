#!/bin/bash
# 运行测试并生成覆盖率报告的脚本

set -e

# 创建测试报告目录
REPORT_DIR="test-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_SUBDIR="${REPORT_DIR}/${TIMESTAMP}"
mkdir -p "${REPORT_SUBDIR}"

echo "=========================================="
echo "运行测试并生成覆盖率报告"
echo "报告将保存到: ${REPORT_SUBDIR}"
echo "=========================================="

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker 未运行，请先启动 Docker"
    exit 1
fi

echo ""
echo "=========================================="
echo "运行后端单元测试和覆盖率"
echo "=========================================="

# 运行后端测试并生成覆盖率报告
docker run --rm \
    -e DJANGO_SETTINGS_MODULE=app.settings_test \
    -v "$(pwd)/src/backend/app:/app" \
    -v "$(pwd)/${REPORT_SUBDIR}:/reports" \
    -w /app \
    minor_review-backend \
    sh -c "
        echo '安装测试依赖...' && \
        pip install pytest pytest-django pytest-cov coverage --quiet >/dev/null 2>&1 && \
        echo '运行后端单元测试和集成测试...' && \
        python -m pytest \
            --cov=list \
            --cov=canteen \
            --cov=post \
            --cov=profile \
            --cov=login \
            --cov=utils \
            --cov-report=term \
            --cov-report=html:/reports/backend-coverage-html \
            --cov-report=xml:/reports/backend-coverage.xml \
            -v --tb=short \
            --ignore=**/migrations/ \
            > /reports/backend-test-results.txt 2>&1 && \
        echo '后端测试完成！'
    "

echo ""
echo "=========================================="
echo "运行前端单元测试和覆盖率"
echo "=========================================="

# 检查前端镜像是否存在
if ! docker images | grep -q "minor_review-frontend"; then
    echo "构建前端镜像..."
    docker-compose build frontend
fi

# 运行前端测试并生成覆盖率报告
echo "检查前端测试文件..."
if [ -d "src/frontend/src" ] && (find src/frontend/src -name "*.test.js" -o -name "*.spec.js" | head -1 | grep -q .); then
    docker run --rm \
        -v "$(pwd)/src/frontend:/app" \
        -v "$(pwd)/${REPORT_SUBDIR}:/reports" \
        -v "$(pwd)/vitest.config.js:/app/vitest.config.js" \
        -w /app \
        minor_review-frontend \
        sh -c "
            echo '安装测试依赖...' && \
            npm install --quiet >/dev/null 2>&1 && \
            echo '安装覆盖率工具...' && \
            npm install --save-dev @vitest/coverage-v8@^1.0.0 --legacy-peer-deps --quiet >/dev/null 2>&1 || \
            npm install --save-dev @vitest/coverage-v8@latest --legacy-peer-deps --quiet >/dev/null 2>&1 || true && \
            echo '运行前端单元测试...' && \
            npx vitest run --coverage \
                --coverage.reporter=text \
                --coverage.reporter=html \
                --coverage.reporter=json \
                --coverage.outputDir=/reports/frontend-coverage \
                --reporter=verbose \
                > /reports/frontend-test-results.txt 2>&1 && \
            echo '前端测试完成！'
        " || {
            echo "前端测试可能失败，但继续生成报告..."
        }
else
    echo "未找到前端测试文件，跳过前端测试..."
    echo "未找到前端测试文件" > "${REPORT_SUBDIR}/frontend-test-results.txt"
fi

echo ""
echo "=========================================="
echo "生成测试摘要报告"
echo "=========================================="

# 提取后端覆盖率信息
BACKEND_COVERAGE=$(grep -E "^TOTAL" "${REPORT_SUBDIR}/backend-test-results.txt" | tail -1 || echo "无法获取覆盖率")
BACKEND_TEST_COUNT=$(grep -E "passed|failed" "${REPORT_SUBDIR}/backend-test-results.txt" | tail -1 || echo "无法获取测试数量")

# 提取前端测试信息
if [ -f "${REPORT_SUBDIR}/frontend-test-results.txt" ]; then
    FRONTEND_TEST_INFO=$(tail -20 "${REPORT_SUBDIR}/frontend-test-results.txt" | grep -E "(Test Files|Tests|PASS|FAIL)" || echo "无法读取前端测试结果")
else
    FRONTEND_TEST_INFO="前端测试文件未生成"
fi

# 生成测试摘要
cat > "${REPORT_SUBDIR}/test-summary.md" << EOF
# 测试报告摘要

**生成时间**: $(date)
**报告目录**: ${REPORT_SUBDIR}

## 后端测试结果

### 测试统计
${BACKEND_TEST_COUNT}

### 代码覆盖率
${BACKEND_COVERAGE}

### 详细结果
\`\`\`
$(tail -30 "${REPORT_SUBDIR}/backend-test-results.txt" | grep -E "(PASSED|FAILED|ERROR|passed|failed|error|TOTAL|coverage|^[a-z]+/)" || echo "无法读取后端测试结果")
\`\`\`

## 前端测试结果

${FRONTEND_TEST_INFO}

### 详细结果
\`\`\`
$(tail -30 "${REPORT_SUBDIR}/frontend-test-results.txt" || echo "无法读取前端测试结果")
\`\`\`

## 覆盖率报告位置

- **后端 HTML 覆盖率报告**: \`backend-coverage-html/index.html\`
- **后端 XML 覆盖率报告**: \`backend-coverage.xml\`
- **前端覆盖率报告**: \`frontend-coverage/index.html\` (如果存在)

## 详细测试结果文件

- **后端测试详细结果**: \`backend-test-results.txt\`
- **前端测试详细结果**: \`frontend-test-results.txt\`

## 查看报告

### 在浏览器中查看后端覆盖率
\`\`\`bash
open ${REPORT_SUBDIR}/backend-coverage-html/index.html
\`\`\`

### 在浏览器中查看前端覆盖率（如果存在）
\`\`\`bash
open ${REPORT_SUBDIR}/frontend-coverage/index.html
\`\`\`
EOF

# 生成简化的覆盖率摘要
cat > "${REPORT_SUBDIR}/coverage-summary.txt" << EOF
测试覆盖率摘要
生成时间: $(date)

后端代码覆盖率:
${BACKEND_COVERAGE}

前端测试状态:
${FRONTEND_TEST_INFO}
EOF

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo "测试报告已保存到: ${REPORT_SUBDIR}"
echo ""
echo "查看测试摘要:"
echo "  cat ${REPORT_SUBDIR}/test-summary.md"
echo ""
echo "查看后端覆盖率报告:"
echo "  open ${REPORT_SUBDIR}/backend-coverage-html/index.html"
echo ""
echo "查看前端覆盖率报告:"
echo "  open ${REPORT_SUBDIR}/frontend-coverage/index.html"
echo ""

