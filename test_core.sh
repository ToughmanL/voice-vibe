#!/bin/bash
# 简单流程测试 - 使用 curl

echo "============================================================"
echo "简单流程测试"
echo "============================================================"

# 测试1: 健康检查
echo ""
echo "【测试1/3】健康检查"
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q '"status":"ok"'; then
    echo "✅ 服务正常"
    echo "$HEALTH" | python3 -m json.tool
else
    echo "❌ 服务异常"
    echo "$HEALTH"
    exit 1
fi

# 测试2: 匹配功能
echo ""
echo "【测试2/3】匹配功能测试"
MATCH=$(curl -s -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "profile": {
      "age": 25,
      "gender": "male",
      "interests": ["coding", "music"],
      "bio": "程序员"
    },
    "text": "你好"
  }')

if echo "$MATCH" | grep -q '"success"'; then
    echo "✅ 匹配成功"
    echo "$MATCH" | python3 -m json.tool | head -20
else
    echo "❌ 匹配失败"
    echo "$MATCH"
fi

# 测试3: WebSocket 对话
echo ""
echo "【测试3/3】WebSocket 对话测试"
echo "（需要安装 wscat: npm install -g wscat）"
echo "手动测试命令:"
echo "wscat -c ws://localhost:8000/ws/chat/test"
echo '然后发送: {"type":"text","content":"你好"}'

echo ""
echo "============================================================"
echo "✅ 基础测试完成"
echo "============================================================"
echo ""
echo "🌐 现在可以打开浏览器体验完整功能:"
echo "   http://localhost:8000"
echo ""
echo "📝 在浏览器中:"
echo "   1. 输入文字测试对话"
echo "   2. 点击录音测试语音"
echo ""
