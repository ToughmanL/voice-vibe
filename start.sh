#!/bin/bash
# AI 语音匹配平台启动脚本

echo "============================================================"
echo "  AI语音匹配平台 - MVP Demo"
echo "============================================================"

# 切换到项目目录
cd "$(dirname "$0")"

# 检查配置文件
if [ ! -f "config/api_keys.json" ]; then
    echo "❌ 错误: 找不到配置文件 config/api_keys.json"
    exit 1
fi

# 检查依赖
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 启动服务
echo ""
echo "🚀 启动服务器..."
echo ""

exec python3 src/demo.py
