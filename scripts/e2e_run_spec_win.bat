@echo off
REM Windows 批处理脚本：本地运行 Cypress 测试
REM 用法: e2e_run_spec_win.bat [auth|canteen|community|profile|all]

SETLOCAL ENABLEDELAYEDEXPANSION

REM 默认参数为 all
SET NAME=%1
IF "%NAME%"=="" SET NAME=all

REM 选择 spec 路径
IF "%NAME%"=="auth" SET SPEC=cypress/e2e/auth.cy.js
IF "%NAME%"=="canteen" SET SPEC=cypress/e2e/canteen.cy.js
IF "%NAME%"=="community" SET SPEC=cypress/e2e/community.cy.js
IF "%NAME%"=="profile" SET SPEC=cypress/e2e/profile.cy.js
IF "%NAME%"=="all" SET SPEC=cypress/e2e/**/*.cy.js

REM 检查参数合法性
IF NOT "%NAME%"=="auth" IF NOT "%NAME%"=="canteen" IF NOT "%NAME%"=="community" IF NOT "%NAME%"=="profile" IF NOT "%NAME%"=="all" (
    echo Usage: %0 [auth|canteen|community|profile|all]
    exit /b 2
)

echo Running Cypress spec for: %NAME% -- ^(%SPEC%^

REM 运行 Cypress 测试
npx cypress run --spec "%SPEC%" --reporter spec
SET EXIT_CODE=%ERRORLEVEL%

echo.
echo ========== Test Summary ==========
REM 统计通过/失败/挂起数（仅简单输出，详细统计可用 grep/awk 工具）
REM Windows 下可直接查看命令行输出

echo.
echo Artifacts (in repo):
echo   - ./cypress/videos
echo   - ./cypress/screenshots

exit /b %EXIT_CODE%
