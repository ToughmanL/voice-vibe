#!/usr/bin/env python3
"""
测试 websockets 库的正确用法
"""
import asyncio
import websockets

async def test_websockets_api():
    """测试 websockets 15.0.1 的 API"""
    
    # 使用一个公开的 WebSocket 测试服务器
    test_url = "wss://echo.websocket.org"
    
    print(f"websockets 版本: {websockets.__version__}")
    print(f"\n连接到: {test_url}")
    
    try:
        async with websockets.connect(test_url, open_timeout=10) as ws:
            print(f"\n✅ 连接成功！")
            
            # 检查连接对象的属性
            print(f"\n连接对象类型: {type(ws)}")
            print(f"连接对象属性:")
            
            # 列出所有属性
            attrs = [attr for attr in dir(ws) if not attr.startswith('_')]
            for attr in attrs:
                try:
                    value = getattr(ws, attr)
                    if not callable(value):
                        print(f"  {attr}: {value}")
                except:
                    pass
            
            # 测试状态检查方法
            print(f"\n状态检查:")
            print(f"  ws.state: {ws.state}")
            print(f"  ws.state.name: {ws.state.name}")
            
            # 测试发送和接收
            print(f"\n测试发送消息...")
            await ws.send("Hello!")
            response = await ws.recv()
            print(f"  收到回复: {response}")
            
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websockets_api())
