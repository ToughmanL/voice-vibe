#!/bin/bash
# 完整流程测试 - 使用 curl

echo "============================================================"
echo "AI 语音匹配平台 - 完整流程测试"
echo "============================================================"
echo ""

# 步骤1: 健康检查
echo "步骤 1/4: 健康检查"
echo "------------------------------------------------------------"
HEALTH=$(curl -s http://localhost:8000/health)
echo "$HEALTH" | python3 -m json.tool
echo ""

# 步骤2: WebSocket 连接测试
echo "步骤 2/4: WebSocket 连接测试"
echo "------------------------------------------------------------"
echo "✅ WebSocket 端点: ws://localhost:8000/ws/chat/<session_id>"
echo "   (需要在浏览器或 WebSocket 客户端中测试)"
echo ""

# 步骤3: 匹配功能测试
echo "步骤 3/4: 匹配功能测试"
echo "------------------------------------------------------------"
MATCH_RESULT=$(curl -s -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "profile": {
      "age": 25,
      "gender": "male",
      "interests": ["coding", "music"],
      "bio": "程序员"
    },
    "text": "我想找朋友"
  }')

echo "$MATCH_RESULT" | python3 -m json.tool
echo ""

# 步骤4: 完整对话流程
echo "步骤 4/4: 完整对话流程（WebSocket）"
echo "------------------------------------------------------------"
echo "使用 Python WebSocket 客户端测试..."

python3 << 'PYEOF'
import asyncio
import websockets
import json

async def test_chat():
    try:
        ws_url = "ws://localhost:8000/ws/chat/flow_test"
        async with websockets.connect(ws_url, open_timeout=10) as ws:
            # 发送消息
            test_msg = "你好，请介绍一下你自己"
            print(f"📤 发送: {test_msg}")

            await ws.send(json.dumps({
                "type": "text",
                "content": test_msg
            }))

            # 接收回复
            print("⏳ 等待回复...")
            response = await asyncio.wait_for(ws.recv(), timeout=30)
            data = json.loads(response)

            content = data.get('content', '')
            print(f"✅ 收到回复: {content[:150]}...")

            return True

    except asyncio.TimeoutError:
        print("❌ 等待回复超时")
        return False
    except Exception as e:
        print(f"❌ 对话失败: {e}")
        return False

result = asyncio.run(test_chat())
PYEOF

echo ""
echo "============================================================"
echo "✅ 测试完成"
echo "============================================================"
echo ""
echo "🌐 现在可以在浏览器中体验完整功能:"
echo "   http://localhost:8000"
echo ""
