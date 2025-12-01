@echo off
chcp 65001 > nul
title 食堂数据生成工具

cd /d %~dp0

echo ============================================================
echo            食堂数据自动生成工具
echo ============================================================
echo.
echo 当前目录: %CD%
echo.
echo 请选择操作:
echo.
echo   1. 快速生成数据（每餐厅40-60道菜）
echo   2. 生成大量数据（每餐厅100道菜）
echo   3. 生成少量数据（每餐厅20道菜）
echo   4. 查看数据统计
echo   5. 清空所有数据（不生成新数据）
echo   6. 清空并重新生成数据
echo   7. 下载菜品图片
echo   8. 查看帮助信息
echo   0. 退出
echo.
echo ============================================================
set /p choice=请输入选项 (0-8): 

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto large
if "%choice%"=="3" goto small
if "%choice%"=="4" goto stats
if "%choice%"=="5" goto clear_only
if "%choice%"=="6" goto clear_regen
if "%choice%"=="7" goto download
if "%choice%"=="8" goto help
if "%choice%"=="0" goto end
goto menu

:quick
cls
echo.
echo 正在快速生成数据...
echo.
python generate_canteen_data.py
echo.
pause
exit

:large
cls
echo.
echo 正在生成大量数据（每餐厅100道菜）...
echo.
python generate_canteen_data.py -n 100
echo.
pause
exit

:small
cls
echo.
echo 正在生成少量数据（每餐厅20道菜）...
echo.
python generate_canteen_data.py -n 20
echo.
pause
exit

:stats
cls
echo.
python generate_canteen_data.py --stats
echo.
pause
exit

:clear_only
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
    exit
)

python generate_canteen_data.py --clear-only
echo.
pause
exit

:clear_regen
cls
echo.
echo ============================================================
echo                        警告
echo ============================================================
echo.
echo 此操作将删除所有数据并重新生成！
echo 此操作不可恢复！
echo.
set /p confirm=确定要继续吗？(输入 YES 确认): 

if not "%confirm%"=="YES" (
    echo.
    echo 操作已取消
    timeout /t 2 > nul
    exit
)

python generate_canteen_data.py --clear
echo.
pause
exit

:download
cls
echo.
echo 正在下载菜品图片...
echo 注意：需要先安装requests库（pip install requests）
echo.
python generate_canteen_data.py --download-images
echo.
pause
exit

:help
cls
echo.
python generate_canteen_data.py --help
echo.
pause
exit

:end
cls
echo.
echo 感谢使用！再见！
echo.
timeout /t 2 > nul
exit
