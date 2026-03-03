#!/usr/bin/env python3
"""
测试科大讯飞 ASR 实际连接
"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from providers.xunfei.asr_client import XunfeiASRClient
from config_loader import ConfigLoader

async def test_asr_connection():
    """测试ASR连接"""
    print("="*60)
    print("测试科大讯飞 ASR 实际连接")
    print("="*60)
    
    # 加载配置
    config_loader = ConfigLoader()
    xunfei_config = config_loader.xunfei_asr
    
    print(f"\n✅ 配置加载成功")
    print(f"APPID: {xunfei_config['appid']}")
    print(f"API Key: {xunfei_config['api_key'][:10]}...")
    
    # 创建ASR客户端
    asr_client = XunfeiASRClient(
        appid=xunfei_config['appid'],
        api_key=xunfei_config['api_key'],
        api_secret=xunfei_config['api_secret']
    )
    
    print(f"\n🔗 生成的鉴权URL:")
    auth_url = asr_client._generate_auth_url()
    print(f"{auth_url[:100]}...")
    
    # 测试连接（不发送音频）
    print(f"\n📡 测试WebSocket连接...")
    try:
        await asr_client._connect()
        
        if asr_client.ws and not asr_client.ws.closed:
            print("✅ WebSocket连接成功建立！")
            
            # 关闭连接
            await asr_client.close()
            print("✅ 连接已关闭")
            return True
        else:
            print("❌ WebSocket连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_asr_with_silence():
    """测试ASR识别静音音频"""
    print("\n" + "="*60)
    print("测试 ASR 识别静音音频")
    print("="*60)
    
    # 加载配置
    config_loader = ConfigLoader()
    xunfei_config = config_loader.xunfei_asr
    
    # 创建ASR客户端
    asr_client = XunfeiASRClient(
        appid=xunfei_config['appid'],
        api_key=xunfei_config['api_key'],
        api_secret=xunfei_config['api_secret']
    )
    
    # 生成1秒的静音音频（16kHz, 16bit, mono）
    silence_audio = b'\x00\x00' * 16000
    
    print(f"\n🎵 生成了 {len(silence_audio)} 字节的静音音频")
    
    try:
        print(f"\n📡 开始识别...")
        
        result = await asr_client.transcribe(silence_audio)
        
        print(f"\n✅ 识别完成")
        print(f"结果: '{result}' (静音音频应该返回空字符串)")
        
        return True
        
    except Exception as e:
        print(f"❌ 识别失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("\n🚀 开始测试...\n")
    
    # 测试1: 连接测试
    success1 = await test_asr_connection()
    
    # 测试2: 识别测试（如果连接成功）
    success2 = False
    if success1:
        success2 = await test_asr_with_silence()
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    print(f"连接测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"识别测试: {'✅ 通过' if success2 else '❌ 失败'}")
    print("="*60)
    
    if success1 and success2:
        print("\n🎉 所有测试通过！ASR 功能正常工作！")
    elif success1:
        print("\n✅ 连接正常，但识别测试失败（可能需要真实音频）")
    else:
        print("\n❌ 连接失败，请检查网络和配置")

if __name__ == "__main__":
    asyncio.run(main())
