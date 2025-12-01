#!/bin/bash

# 菜品数据快速生成脚本 (Linux/macOS)
# 使用方法: ./quick_generate.sh

echo "========================================"
echo "食堂菜品数据生成器"
echo "========================================"
echo ""

show_menu() {
    echo "请选择操作:"
    echo ""
    echo "[1] 快速生成 (每个餐厅50道菜)"
    echo "[2] 大量生成 (每个餐厅100道菜)"
    echo "[3] 小量生成 (每个餐厅20道菜)"
    echo "[4] 清空并重新生成 (每个餐厅50道菜)"
    echo "[5] 查看数据统计"
    echo "[6] 自定义生成"
    echo "[0] 退出"
    echo ""
}

while true; do
    show_menu
    read -p "请输入选项 (0-6): " choice
    
    case $choice in
        1)
            echo ""
            echo "正在生成数据 (每个餐厅50道菜)..."
            python generate_dishes.py
            ;;
        2)
            echo ""
            echo "正在生成数据 (每个餐厅100道菜)..."
            python batch_generate_dishes.py -n 100
            ;;
        3)
            echo ""
            echo "正在生成数据 (每个餐厅20道菜)..."
            python batch_generate_dishes.py -n 20
            ;;
        4)
            echo ""
            echo "⚠️  警告: 这将删除所有现有菜品数据！"
            read -p "确定继续吗? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                python batch_generate_dishes.py -n 50 --clear
            else
                echo "已取消操作"
            fi
            ;;
        5)
            echo ""
            python batch_generate_dishes.py --stats
            ;;
        6)
            echo ""
            echo "自定义生成"
            read -p "请输入每个餐厅生成的菜品数量: " num
            read -p "是否清空现有数据? (yes/no): " clear_choice
            echo ""
            if [ "$clear_choice" = "yes" ]; then
                python batch_generate_dishes.py -n "$num" --clear
            else
                python batch_generate_dishes.py -n "$num"
            fi
            ;;
        0)
            echo ""
            echo "感谢使用！再见~"
            echo ""
            exit 0
            ;;
        *)
            echo "无效选项，请重新选择"
            continue
            ;;
    esac
    
    echo ""
    echo "========================================"
    echo "✅ 操作完成！"
    echo "========================================"
    echo ""
    read -p "是否继续其他操作? (yes/no): " again
    if [ "$again" != "yes" ]; then
        echo ""
        echo "感谢使用！再见~"
        echo ""
        exit 0
    fi
    echo ""
done
