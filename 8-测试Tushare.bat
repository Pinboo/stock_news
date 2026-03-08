@echo off
chcp 65001 >nul
echo ========================================
echo 测试 Tushare 配置
echo ========================================
echo.
echo Tushare 是专业的金融数据接口
echo 数据稳定、质量高、免费使用
echo.
echo 需要先注册获取 Token
echo 注册地址: https://tushare.pro/register
echo.
echo ========================================
echo.

python test_tushare.py

echo.
pause
