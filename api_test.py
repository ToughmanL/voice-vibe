#!/usr/bin/env python3
"""
API 测试脚本
"""
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def test_api():
    """测试 REST API"""
    print("="*60)
    print("AI 语音匹配平台 API 测试")
    print("="*60)
    
    # 1. 测试根路径
    print("\n1. 测试主页...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            print(f"✅ 主页访问成功: {response.status_code}")
    except Exception as e:
        print(f"❌ 主页访问失败: {e}")
    
    # 2. 测试健康检查
    print("\n2. 测试健康检查...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            print(f"✅ 健康检查: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 3. 测试匹配接口
    print("\n3. 测试匹配接口...")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{BASE_URL}/api/match",
                json={
                    "user_id": "test_user_001",
                    "profile": {
                        "age": 25,
                        "gender": "male",
                        "interests": ["music", "coding", "reading"],
                        "bio": "喜欢音乐和编程的程序员"
                    },
                    "text": "你好，我想找志同道合的朋友"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 匹配成功!")
                print(f"   匹配数量: {len(result.get('matches', []))}")
                
                for match in result.get('matches', []):
                    print(f"   - 用户 {match['user_id']}: {match['similarity']:.2%}")
                    print(f"     理由: {match['reason'][:100]}...")
            else:
                print(f"❌ 匹配失败: {response.status_code}")
                print(f"   错误: {response.text}")
                
    except Exception as e:
        print(f"❌ 匹配测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 测试 WebSocket 对话
    print("\n4. 测试 WebSocket 对话...")
    try:
        import websockets
        
        async with websockets.connect(
            f"ws://localhost:8000/ws/chat/test_session",
            open_timeout=10
        ) as ws:
            # 发送消息
            await ws.send(json.dumps({
                "type": "text",
                "content": "你好，介绍一下你自己"
            }))
            
            # 接收回复
            response = await asyncio.wait_for(ws.recv(), timeout=30)
            result = json.loads(response)
            
            print(f"✅ WebSocket 对话成功!")
            print(f"   回复: {result.get('content', '')[:200]}...")
                
    except Exception as e:
        print(f"❌ WebSocket 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("API 测试完成")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_api())
