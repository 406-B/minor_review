#!/bin/bash
# 在 Docker 环境中运行测试的脚本（增强版 - 支持详细日志和后台执行）

# 配置
LOG_DIR="test_logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/test_${TIMESTAMP}.log"
FAILED_LOG="${LOG_DIR}/failed_${TIMESTAMP}.log"
SUMMARY_LOG="${LOG_DIR}/summary_${TIMESTAMP}.log"

# 解析参数
RUN_IN_BACKGROUND=false
if [[ "$1" == "--background" ]] || [[ "$1" == "-b" ]]; then
    RUN_IN_BACKGROUND=true
fi

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_failed() {
    echo "$1" >> "$FAILED_LOG"
}

log_summary() {
    echo "$1" >> "$SUMMARY_LOG"
}

# 运行测试的函数
run_tests() {
    log "=========================================="
    log "在 Docker 环境中运行单元测试"
    log "=========================================="

    # 检查 Docker 是否运行
    if ! docker info > /dev/null 2>&1; then
        log "错误: Docker 未运行，请先启动 Docker"
        exit 1
    fi

    # 创建网络（如果不存在）
    log "创建 Docker 网络..."
    docker network create minor_review_backend_net 2>/dev/null || log "网络已存在"

    # 检查后端镜像是否存在
    if ! docker images | grep -q "minor_review-backend"; then
        log "构建后端镜像..."
        docker build -t minor_review-backend ./src/backend 2>&1 | tee -a "$LOG_FILE"
    fi

    log ""
    log "=========================================="
    log "运行后端单元测试"
    log "=========================================="

    # 运行测试并捕获输出
    TEST_OUTPUT=$(docker run --rm \
        --network minor_review_backend_net \
        --entrypoint="" \
        -e DJANGO_SETTINGS_MODULE=app.settings_test \
        -v "$(pwd)/src/backend/app:/app" \
        minor_review-backend \
        sh -c "
            echo '安装测试依赖...' && \
            pip install pytest pytest-django pytest-cov coverage --quiet && \
            echo '运行单元测试...' && \
            cd /app && \
            python -m pytest -v --tb=long 2>&1
        " 2>&1)

    # 保存完整输出
    echo "$TEST_OUTPUT" >> "$LOG_FILE"
    echo "$TEST_OUTPUT"

    # 提取失败案例的详细信息
    log ""
    log "=========================================="
    log "分析失败案例..."
    log "=========================================="

    # 提取所有失败案例
    FAILED_TESTS=$(echo "$TEST_OUTPUT" | grep -E "FAILED|ERROR" | grep -E "::" | sed 's/^[[:space:]]*//')

    if [ -n "$FAILED_TESTS" ]; then
        log "发现失败案例，提取详细信息..."
        echo "" >> "$FAILED_LOG"
        echo "==========================================" >> "$FAILED_LOG"
        echo "失败案例详细信息 - $(date)" >> "$FAILED_LOG"
        echo "==========================================" >> "$FAILED_LOG"
        echo "" >> "$FAILED_LOG"

        # 为每个失败案例提取详细信息
        while IFS= read -r test_line; do
            if [[ "$test_line" =~ FAILED|ERROR ]]; then
                # 提取测试路径
                TEST_PATH=$(echo "$test_line" | grep -oE '[a-zA-Z0-9_/]+::[a-zA-Z0-9_]+::[a-zA-Z0-9_]+')

                if [ -n "$TEST_PATH" ]; then
                    log "提取失败案例: $TEST_PATH"
                    echo "" >> "$FAILED_LOG"
                    echo "========================================" >> "$FAILED_LOG"
                    echo "失败案例: $TEST_PATH" >> "$FAILED_LOG"
                    echo "========================================" >> "$FAILED_LOG"

                    # 提取该测试的详细错误信息
                    echo "$TEST_OUTPUT" | grep -A 50 "$TEST_PATH" | head -60 >> "$FAILED_LOG"
                    echo "" >> "$FAILED_LOG"
                fi
            fi
        done <<< "$FAILED_TESTS"

        log "失败案例详细信息已保存到: $FAILED_LOG"
    else
        log "没有发现失败案例！"
    fi

    # 生成摘要
    log ""
    log "=========================================="
    log "生成测试摘要..."
    log "=========================================="

    TOTAL=$(echo "$TEST_OUTPUT" | grep -E "passed|failed|error" | tail -1 | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -E "passed|failed|error" | tail -1 | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "0")
    ERROR=$(echo "$TEST_OUTPUT" | grep -E "passed|failed|error" | tail -1 | grep -oE '[0-9]+ error' | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -E "passed|failed|error" | tail -1 | grep -oE '[0-9]+ skipped' | grep -oE '[0-9]+' || echo "0")

    {
        echo "=========================================="
        echo "测试摘要 - $(date)"
        echo "=========================================="
        echo "总通过: $TOTAL"
        echo "总失败: $FAILED"
        echo "总错误: $ERROR"
        echo "总跳过: $SKIPPED"
        echo ""
        echo "完整日志: $LOG_FILE"
        echo "失败详情: $FAILED_LOG"
        echo ""
        if [ -n "$FAILED_TESTS" ]; then
            echo "失败案例列表:"
            echo "$FAILED_TESTS" | while IFS= read -r line; do
                echo "  - $line"
            done
        fi
    } | tee "$SUMMARY_LOG"

    log ""
    log "=========================================="
    log "测试完成！"
    log "=========================================="
    log "日志文件:"
    log "  - 完整日志: $LOG_FILE"
    log "  - 失败详情: $FAILED_LOG"
    log "  - 测试摘要: $SUMMARY_LOG"
}

# 主执行逻辑
if [ "$RUN_IN_BACKGROUND" = true ]; then
    echo "在后台运行测试..."
    echo "日志将保存到: $LOG_FILE"
    nohup "$0" > "${LOG_DIR}/background_${TIMESTAMP}.out" 2>&1 &
    PID=$!
    echo "测试已在后台运行，PID: $PID"
    echo "查看进度: tail -f ${LOG_DIR}/background_${TIMESTAMP}.out"
    echo "查看日志: tail -f $LOG_FILE"
    echo $PID > "${LOG_DIR}/test_${TIMESTAMP}.pid"
    echo "使用以下命令查看失败案例: ./view-failed-tests.sh"
else
    run_tests
fi
