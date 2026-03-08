@echo off
chcp 65001 >nul
echo ========================================
echo 查看服务运行状态
echo ========================================
echo.

echo 【Python 进程】
tasklist | find "python.exe"
if %errorlevel% neq 0 (
    echo   ✗ 没有运行中的 Python 进程
)

echo.
echo 【命令行窗口】
tasklist /V /FI "IMAGENAME eq cmd.exe" | find "定时推送" >nul
if %errorlevel% equ 0 (
    echo   ✓ 定时推送服务 - 运行中
) else (
    echo   ✗ 定时推送服务 - 未运行
)

tasklist /V /FI "IMAGENAME eq cmd.exe" | find "聊天机器人" >nul
if %errorlevel% equ 0 (
    echo   ✓ 聊天机器人服务 - 运行中
) else (
    echo   ✗ 聊天机器人服务 - 未运行
)

echo.
echo ========================================
echo.
pause
