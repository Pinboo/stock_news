@echo off
chcp 65001 >nul
echo ========================================
echo 停止所有服务
echo ========================================
echo.

echo 正在查找运行中的服务...
echo.

tasklist /FI "WINDOWTITLE eq 定时推送服务*" 2>nul | find "cmd.exe" >nul
if %errorlevel% equ 0 (
    echo ✓ 找到定时推送服务
) else (
    echo ✗ 定时推送服务未运行
)

tasklist /FI "WINDOWTITLE eq 聊天机器人服务*" 2>nul | find "cmd.exe" >nul
if %errorlevel% equ 0 (
    echo ✓ 找到聊天机器人服务
) else (
    echo ✗ 聊天机器人服务未运行
)

echo.
echo ========================================
echo.
echo 💡 提示：
echo   要停止服务，请直接关闭对应的命令行窗口
echo   或在窗口中按 Ctrl+C
echo.
echo 如果窗口无法关闭，可以使用任务管理器：
echo   1. 按 Ctrl+Shift+Esc 打开任务管理器
echo   2. 找到 Python 进程
echo   3. 右键 → 结束任务
echo.
pause
