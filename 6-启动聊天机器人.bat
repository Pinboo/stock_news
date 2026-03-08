@echo off
chcp 65001 >nul
echo ========================================
echo 启动钉钉聊天机器人（Stream模式）
echo ========================================
echo.
echo 功能：在钉钉群里@机器人聊天
echo.
echo 支持的命令：
echo   @机器人 + 股票代码（如 000001）
echo   @机器人 大盘
echo   @机器人 新闻
echo   @机器人 帮助
echo.
echo ⚠️  注意：
echo   1. 需要先在钉钉开发者后台开通Stream模式
echo   2. 详细配置请查看：钉钉Stream模式配置.md
echo   3. 保持此窗口运行，机器人才能工作
echo.
echo ========================================
echo.

python dingtalk_chat_bot.py

pause
