#!/bin/bash

# 设置UTF-8编码
export LANG=zh_CN.UTF-8

# 菜品数据生成工具 V2

show_menu() {
    clear
    echo "============================================================"
    echo "            菜品数据自动生成工具 V2"
    echo "============================================================"
    echo ""
    echo "请选择操作:"
    echo ""
    echo "  1. 快速生成 (推荐) - 每餐厅生成40-60道菜 + 楼层窗口"
    echo "  2. 大量生成 - 每餐厅生成80-120道菜 + 楼层窗口"
    echo "  3. 小量生成 - 每餐厅生成20-30道菜 + 楼层窗口"
    echo "  4. 下载菜品图片 (需要requests库)"
    echo "  5. 查看数据统计和验证"
    echo "  6. 清空所有数据并重新生成"
    echo "  0. 退出"
    echo ""
    echo "============================================================"
    read -p "请输入选项 (0-6): " choice
    echo ""
}

quick_generate() {
    clear
    echo ""
    echo "正在快速生成菜品数据..."
    echo ""
    python generate_dishes_v2.py
    echo ""
    read -p "按回车键返回菜单..."
}

large_generate() {
    clear
    echo ""
    echo "正在大量生成菜品数据..."
    echo "注意: 这会修改脚本中的数量范围"
    echo ""
    echo "你需要手动编辑 generate_dishes_v2.py"
    echo "将第302行的 random.randint(40, 60) 改为 random.randint(80, 120)"
    echo ""
    read -p "按回车键返回菜单..."
}

small_generate() {
    clear
    echo ""
    echo "正在小量生成菜品数据..."
    echo "注意: 这会修改脚本中的数量范围"
    echo ""
    echo "你需要手动编辑 generate_dishes_v2.py"
    echo "将第302行的 random.randint(40, 60) 改为 random.randint(20, 30)"
    echo ""
    read -p "按回车键返回菜单..."
}

download_images() {
    clear
    echo ""
    echo "正在下载菜品图片..."
    echo "注意: 需要先安装requests库"
    echo ""
    
    # 检查requests库
    python -c "import requests" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "requests库未安装，正在安装..."
        pip install requests
        if [ $? -ne 0 ]; then
            echo ""
            echo "安装失败，请手动运行: pip install requests"
            echo ""
            read -p "按回车键返回菜单..."
            return
        fi
    fi
    
    echo ""
    python download_dish_images.py
    echo ""
    read -p "按回车键返回菜单..."
}

show_stats() {
    clear
    echo ""
    echo "正在查看数据统计..."
    echo ""
    python validate_dishes.py
    echo ""
    echo "============================================================"
    echo ""
    read -p "是否查看样本菜品？(Y/N): " sample
    
    if [ "$sample" = "Y" ] || [ "$sample" = "y" ]; then
        echo ""
        python validate_dishes.py --sample
    fi
    
    echo ""
    read -p "按回车键返回菜单..."
}

clear_and_generate() {
    clear
    echo ""
    echo "============================================================"
    echo "                        警告"
    echo "============================================================"
    echo ""
    echo "此操作将删除所有菜品、标签、楼层和窗口数据！"
    echo "此操作不可恢复！"
    echo ""
    read -p "确定要继续吗？(输入 YES 确认): " confirm
    
    if [ "$confirm" != "YES" ]; then
        echo ""
        echo "操作已取消"
        sleep 2
        return
    fi
    
    echo ""
    echo "正在清空数据..."
    python manage.py shell -c "from list.models import Dish, Tag, Floor, Window; Dish.objects.all().delete(); Tag.objects.all().delete(); Floor.objects.all().delete(); Window.objects.all().delete(); print('数据已清空')"
    
    echo ""
    echo "正在重新生成数据..."
    python generate_dishes_v2.py
    
    echo ""
    read -p "按回车键返回菜单..."
}

# 主循环
while true; do
    show_menu
    
    case $choice in
        1)
            quick_generate
            ;;
        2)
            large_generate
            ;;
        3)
            small_generate
            ;;
        4)
            download_images
            ;;
        5)
            show_stats
            ;;
        6)
            clear_and_generate
            ;;
        0)
            clear
            echo ""
            echo "感谢使用！再见！"
            echo ""
            sleep 2
            exit 0
            ;;
        *)
            echo "无效选项，请重新选择"
            sleep 1
            ;;
    esac
done
