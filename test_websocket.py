#!/usr/bin/env python3
"""
WebSocket客户端测试脚本
"""
import asyncio
import websockets
import json
import sys

async def test_chat():
    uri = "ws://localhost:8000/ws/chat/test_session_123"

    print(f"🔗 连接到: {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 连接成功！")

            # 发送测试消息
            test_message = {
                "type": "text",
                "content": "你好，我是测试用户"
            }

            print(f"📤 发送消息: {test_message}")
            await websocket.send(json.dumps(test_message))

            # 接收回复
            print("⏳ 等待回复...")
            response = await websocket.recv()
            data = json.loads(response)

            print(f"\n📥 收到回复:")
            print(f"类型: {data.get('type')}")
            print(f"内容: {data.get('content', data.get('data', '')[:100])}")

            if data.get('type') == 'audio':
                print(f"🎵 音频数据: {len(data.get('data', ''))} 字符")

            print("\n✅ 测试成功！")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat())
