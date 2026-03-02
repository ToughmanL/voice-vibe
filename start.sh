#!/bin/bash

# 快速启动脚本

echo "🎵 AI语音匹配平台 - 快速启动"
echo "================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 检查配置文件
if [ ! -f "config/api_keys.json" ]; then
    echo "⚠️  警告：未找到配置文件"
    echo "📋 复制配置模板..."
    cp config/api_keys.example.json config/api_keys.json
    echo ""
    echo "❗ 请先编辑 config/api_keys.json 填入你的API密钥："
    echo "   - 科大讯飞：https://www.xfyun.cn/"
    echo "   - Kimi：https://platform.moonshot.cn/"
    echo ""
    read -p "按Enter继续..."
fi

# 启动服务
echo ""
echo "🚀 启动服务..."
echo "================================"
cd src
python demo.py
