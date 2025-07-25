@echo off
chcp 65001 >nul
echo 🚀 TTS GUI程序打包工具
echo ================================
echo.

echo 📋 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo 📦 开始打包程序...
python build_exe.py

echo.
echo ✅ 打包完成！
echo 📁 请查看dist目录中的exe文件
echo.
pause
