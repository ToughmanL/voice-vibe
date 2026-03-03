#!/usr/bin/env python3
"""
简单流程测试 - 只测试核心功能
"""
import asyncio
import httpx
import websockets
import json

async def main():
    print("="*60)
    print("简单流程测试")
    print("="*60)

    # 测试1: 健康检查
    print("\n【测试1/3】健康检查")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:8000/health", timeout=5)
            if r.status_code == 200:
                print("✅ 服务正常")
            else:
                print(f"❌ 服务异常: {r.status_code}")
                return
    except Exception as e:
        print(f"❌ 无法连接: {e}")
        print("请先启动服务: python3 src/demo.py")
        return

    # 测试2: 文字对话
    print("\n【测试2/3】文字对话测试")
    try:
        ws = await websockets.connect(
            "ws://localhost:8000/ws/chat/test",
            open_timeout=10
        )

        # 发送消息
        await ws.send(json.dumps({
            "type": "text",
            "content": "你好"
        }))
        print("📤 发送: 你好")

        # 接收回复
        response = await asyncio.wait_for(ws.recv(), timeout=30)
        data = json.loads(response)

        if data.get('type') == 'text' and data.get('content'):
            print(f"✅ 收到回复: {data['content'][:50]}...")
        else:
            print(f"⚠️  回复格式异常: {data}")

        await ws.close()

    except asyncio.TimeoutError:
        print("❌ 等待回复超时")
    except Exception as e:
        print(f"❌ 对话失败: {e}")

    # 测试3: 匹配功能
    print("\n【测试3/3】匹配功能测试")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "http://localhost:8000/api/match",
                json={
                    "user_id": "test_user",
                    "profile": {
                        "age": 25,
                        "interests": ["coding", "music"]
                    },
                    "text": "你好"
                }
            )

            if r.status_code == 200:
                data = r.json()
                matches = data.get('matches', [])
                print(f"✅ 找到 {len(matches)} 个匹配")
                if matches:
                    print(f"   最佳匹配: {matches[0].get('user_id')}")
            else:
                print(f"❌ 匹配失败: {r.status_code}")

    except Exception as e:
        print(f"❌ 匹配失败: {e}")

    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)
    print("\n如果所有测试都通过，说明核心功能正常。")
    print("现在可以打开浏览器体验完整功能:")
    print("http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main())
