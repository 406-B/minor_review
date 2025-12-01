@echo off
chcp 65001 > nul
title 菜品数据生成工具 V2

:menu
cls
echo ============================================================
echo            菜品数据自动生成工具 V2
echo ============================================================
echo.
echo 请选择操作:
echo.
echo   1. 快速生成 (推荐) - 每餐厅生成40-60道菜 + 楼层窗口
echo   2. 大量生成 - 每餐厅生成80-120道菜 + 楼层窗口
echo   3. 小量生成 - 每餐厅生成20-30道菜 + 楼层窗口
echo   4. 下载菜品图片 (需要requests库)
echo   5. 查看数据统计和验证
echo   6. 清空所有数据并重新生成
echo   0. 退出
echo.
echo ============================================================
set /p choice=请输入选项 (0-6): 

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto large
if "%choice%"=="3" goto small
if "%choice%"=="4" goto download_images
if "%choice%"=="5" goto stats
if "%choice%"=="6" goto clear
if "%choice%"=="0" goto end
goto menu

:quick
cls
echo.
echo 正在快速生成菜品数据...
echo.
python generate_dishes_v2.py
echo.
echo 按任意键返回菜单...
pause > nul
goto menu

:large
cls
echo.
echo 正在大量生成菜品数据...
echo 注意: 这会修改脚本中的数量范围
echo.
echo 你需要手动编辑 generate_dishes_v2.py
echo 将第302行的 random.randint(40, 60) 改为 random.randint(80, 120)
echo.
echo 按任意键返回菜单...
pause > nul
goto menu

:small
cls
echo.
echo 正在小量生成菜品数据...
echo 注意: 这会修改脚本中的数量范围
echo.
echo 你需要手动编辑 generate_dishes_v2.py
echo 将第302行的 random.randint(40, 60) 改为 random.randint(20, 30)
echo.
echo 按任意键返回菜单...
pause > nul
goto menu

:download_images
cls
echo.
echo 正在下载菜品图片...
echo 注意: 需要先安装requests库
echo.
echo 检查requests库...
python -c "import requests" 2>nul
if errorlevel 1 (
    echo requests库未安装，正在安装...
    pip install requests
    if errorlevel 1 (
        echo.
        echo 安装失败，请手动运行: pip install requests
        echo.
        pause
        goto menu
    )
)
echo.
python download_dish_images.py
echo.
echo 按任意键返回菜单...
pause > nul
goto menu

:stats
cls
echo.
echo 正在查看数据统计...
echo.
python validate_dishes.py
echo.
echo ============================================================
echo.
set /p sample=是否查看样本菜品？(Y/N): 
if /i "%sample%"=="Y" (
    echo.
    python validate_dishes.py --sample
)
echo.
echo 按任意键返回菜单...
pause > nul
goto menu

:clear
cls
echo.
echo ============================================================
echo                        警告
echo ============================================================
echo.
echo 此操作将删除所有菜品、标签、楼层和窗口数据！
echo 此操作不可恢复！
echo.
set /p confirm=确定要继续吗？(输入 YES 确认): 

if not "%confirm%"=="YES" (
    echo.
    echo 操作已取消
    timeout /t 2 > nul
    goto menu
)

echo.
echo 正在清空数据...
python manage.py shell -c "from list.models import Dish, Tag, Floor, Window; Dish.objects.all().delete(); Tag.objects.all().delete(); Floor.objects.all().delete(); Window.objects.all().delete(); print('数据已清空')"

echo.
echo 正在重新生成数据...
python generate_dishes_v2.py

echo.
echo 按任意键返回菜单...
pause > nul
goto menu

:end
cls
echo.
echo 感谢使用！再见！
echo.
timeout /t 2 > nul
exit
