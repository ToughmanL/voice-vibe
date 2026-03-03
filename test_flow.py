#!/usr/bin/env python3
"""
完整流程测试脚本
一步步验证项目的核心功能
"""
import asyncio
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

import websockets


async def test_step_1_health():
    """步骤1: 健康检查"""
    print("\n" + "="*60)
    print("步骤 1/4: 健康检查")
    print("="*60)

    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 服务状态: {data['status']}")
                print(f"\n服务列表:")
                for service, name in data['services'].items():
                    print(f"  - {service}: {name}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n💡 解决方法:")
        print("   1. 确认服务已启动: ./start.sh")
        print("   2. 检查端口 8000 是否被占用")
        return False


async def test_step_2_websocket():
    """步骤2: WebSocket 连接"""
    print("\n" + "="*60)
    print("步骤 2/4: WebSocket 连接测试")
    print("="*60)

    ws_url = "ws://localhost:8000/ws/chat/test_flow_session"

    try:
        print(f"\n连接到: {ws_url}")
        async with websockets.connect(ws_url, open_timeout=10) as ws:
            print("✅ WebSocket 连接成功")
            return True

    except Exception as e:
        print(f"❌ WebSocket 连接失败: {e}")
        return False


async def test_step_3_chat():
    """步骤3: 文字对话"""
    print("\n" + "="*60)
    print("步骤 3/4: 文字对话测试")
    print("="*60)

    ws_url = "ws://localhost:8000/ws/chat/test_chat_session"

    try:
        async with websockets.connect(ws_url, open_timeout=10) as ws:
            # 发送消息
            test_message = "你好，请简单介绍一下你自己"
            print(f"\n📤 发送消息: {test_message}")

            await ws.send(json.dumps({
                "type": "text",
                "content": test_message
            }))

            # 接收回复
            print("⏳ 等待 AI 回复（可能需要几秒）...")

            try:
                response = await asyncio.wait_for(ws.recv(), timeout=30)
                data = json.loads(response)

                print(f"\n✅ 收到回复:")
                print(f"   类型: {data.get('type')}")
                content = data.get('content', '')
                print(f"   内容: {content[:200]}...")

                if content:
                    return True
                else:
                    print("⚠️  回复内容为空")
                    return False

            except asyncio.TimeoutError:
                print("❌ 等待回复超时（30秒）")
                print("💡 可能原因:")
                print("   - Kimi API 响应慢")
                print("   - 网络问题")
                print("   - API 配额用完")
                return False

    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_step_4_match():
    """步骤4: 匹配功能"""
    print("\n" + "="*60)
    print("步骤 4/4: 匹配功能测试")
    print("="*60)

    import httpx

    try:
        print("\n📤 发送匹配请求...")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://localhost:8000/api/match",
                json={
                    "user_id": "test_user_001",
                    "profile": {
                        "age": 25,
                        "gender": "male",
                        "interests": ["coding", "music", "reading"],
                        "bio": "程序员，喜欢编程和音乐"
                    },
                    "text": "我想找志同道合的朋友"
                }
            )

            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ 匹配成功!")
                print(f"   匹配数量: {len(data.get('matches', []))}")

                for i, match in enumerate(data.get('matches', []), 1):
                    print(f"\n   匹配 {i}:")
                    print(f"     用户ID: {match.get('user_id')}")
                    print(f"     相似度: {match.get('score', 0):.2%}")
                    print(f"     理由: {match.get('match_reasons', [])}")

                return True
            else:
                print(f"❌ 匹配失败: {response.status_code}")
                print(f"   错误: {response.text}")
                return False

    except Exception as e:
        print(f"❌ 匹配测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试流程"""
    print("="*60)
    print("AI 语音匹配平台 - 完整流程测试")
    print("="*60)
    print("\n这个脚本会一步步验证项目的核心功能")
    print("请确保服务已启动: ./start.sh\n")

    results = {}

    # 步骤1: 健康检查
    results['health'] = await test_step_1_health()
    if not results['health']:
        print("\n❌ 健康检查失败，请先启动服务")
        return

    # 步骤2: WebSocket 连接
    results['websocket'] = await test_step_2_websocket()
    if not results['websocket']:
        print("\n❌ WebSocket 连接失败")
        return

    # 步骤3: 文字对话
    results['chat'] = await test_step_3_chat()

    # 步骤4: 匹配功能
    results['match'] = await test_step_4_match()

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for step, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {step}: {status}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"\n通过率: {passed}/{total} ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 恭喜！所有核心功能测试通过！")
        print("\n✅ 你已经成功走通了整个流程")
        print("\n🌐 现在可以在浏览器中体验完整功能:")
        print("   http://localhost:8000")
    else:
        print("\n⚠️  部分功能测试失败")
        print("\n💡 建议:")
        print("   1. 查看日志: tail -f nohup.out")
        print("   2. 检查配置: cat config/api_keys.json")
        print("   3. 重启服务: ./start.sh")

    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
