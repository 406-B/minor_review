#!/bin/bash
# 查看最新失败测试案例的脚本

LOG_DIR="test_logs"

if [ ! -d "$LOG_DIR" ]; then
    echo "错误: 日志目录不存在: $LOG_DIR"
    echo "请先运行 ./run-tests.sh"
    exit 1
fi

# 查找最新的失败日志
LATEST_FAILED=$(ls -t ${LOG_DIR}/failed_*.log 2>/dev/null | head -1)
LATEST_SUMMARY=$(ls -t ${LOG_DIR}/summary_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_FAILED" ]; then
    echo "没有找到失败日志文件"
    exit 0
fi

echo "=========================================="
echo "最新测试摘要"
echo "=========================================="
if [ -n "$LATEST_SUMMARY" ]; then
    cat "$LATEST_SUMMARY"
else
    echo "没有找到摘要文件"
fi

echo ""
echo "=========================================="
echo "失败案例详细信息"
echo "=========================================="
echo "文件: $LATEST_FAILED"
echo ""
cat "$LATEST_FAILED"

echo ""
echo "=========================================="
echo "提示: 使用以下命令查看完整日志"
echo "  tail -f ${LOG_DIR}/test_*.log | grep -A 30 FAILED"
echo "=========================================="

