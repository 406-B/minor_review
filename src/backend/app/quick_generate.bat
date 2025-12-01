@echo off
REM 菜品数据快速生成脚本 (Windows)
REM 使用方法: 双击运行或在命令行执行

echo ========================================
echo 食堂菜品数据生成器
echo ========================================
echo.

:menu
echo 请选择操作:
echo.
echo [1] 快速生成 (每个餐厅50道菜)
echo [2] 大量生成 (每个餐厅100道菜)
echo [3] 小量生成 (每个餐厅20道菜)
echo [4] 清空并重新生成 (每个餐厅50道菜)
echo [5] 查看数据统计
echo [6] 自定义生成
echo [0] 退出
echo.

set /p choice="请输入选项 (0-6): "

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto large
if "%choice%"=="3" goto small
if "%choice%"=="4" goto clear
if "%choice%"=="5" goto stats
if "%choice%"=="6" goto custom
if "%choice%"=="0" goto end
goto menu

:quick
echo.
echo 正在生成数据 (每个餐厅50道菜)...
python generate_dishes.py
goto done

:large
echo.
echo 正在生成数据 (每个餐厅100道菜)...
python batch_generate_dishes.py -n 100
goto done

:small
echo.
echo 正在生成数据 (每个餐厅20道菜)...
python batch_generate_dishes.py -n 20
goto done

:clear
echo.
echo ⚠️  警告: 这将删除所有现有菜品数据！
set /p confirm="确定继续吗? (yes/no): "
if /i "%confirm%"=="yes" (
    python batch_generate_dishes.py -n 50 --clear
    goto done
) else (
    echo 已取消操作
    goto menu
)

:stats
echo.
python batch_generate_dishes.py --stats
pause
goto menu

:custom
echo.
echo 自定义生成
set /p num="请输入每个餐厅生成的菜品数量: "
set /p clear_choice="是否清空现有数据? (yes/no): "
echo.
if /i "%clear_choice%"=="yes" (
    python batch_generate_dishes.py -n %num% --clear
) else (
    python batch_generate_dishes.py -n %num%
)
goto done

:done
echo.
echo ========================================
echo ✅ 操作完成！
echo ========================================
echo.
set /p again="是否继续其他操作? (yes/no): "
if /i "%again%"=="yes" goto menu

:end
echo.
echo 感谢使用！再见~
echo.
pause
