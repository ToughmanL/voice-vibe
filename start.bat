@echo off
REM Windows快速启动脚本

echo 🎵 AI语音匹配平台 - 快速启动
echo ================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python
    pause
    exit /b 1
)

echo ✓ Python已安装

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔌 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖...
pip install -q -r requirements.txt

REM 检查配置文件
if not exist "config\api_keys.json" (
    echo ⚠️  警告：未找到配置文件
    echo 📋 复制配置模板...
    copy config\api_keys.example.json config\api_keys.json
    echo.
    echo ❗ 请先编辑 config\api_keys.json 填入你的API密钥
    pause
)

REM 启动服务
echo.
echo 🚀 启动服务...
echo ================================
cd src
python demo.py
