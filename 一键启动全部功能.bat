@echo off
chcp 65001 >nul
echo ========================================
echo 一键启动 A股智能分析系统
echo ========================================
echo.
echo 将同时启动：
echo   1. 定时推送服务（每天 09:00 和 15:30）
echo   2. 聊天机器人服务（实时问答）
echo.
echo 会打开两个命令行窗口，请不要关闭
echo.
echo ========================================
echo.

echo 正在启动定时推送服务...
start "定时推送服务" cmd /k "python main.py"

timeout /t 2 /nobreak >nul

echo 正在启动聊天机器人服务...
start "聊天机器人服务" cmd /k "python dingtalk_chat_bot.py"

echo.
echo ========================================
echo ✅ 启动完成！
echo ========================================
echo.
echo 已打开两个窗口：
echo   - 定时推送服务
echo   - 聊天机器人服务
echo.
echo 💡 提示：
echo   - 保持两个窗口运行
echo   - 关闭窗口会停止对应服务
echo   - 按 Ctrl+C 可以停止服务
echo.
pause
