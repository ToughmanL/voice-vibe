#!/usr/bin/env python3
"""
快速测试脚本
用于快速验证连接是否恢复
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from providers.xunfei.asr_client import XunfeiASRClient
from config_loader import ConfigLoader


async def quick_test():
    """快速测试连接和识别"""
    print("="*60)
    print("科大讯飞 ASR 快速测试")
    print("="*60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 加载配置
    config_loader = ConfigLoader()
    xunfei_config = config_loader.xunfei_asr
    
    # 创建ASR客户端
    asr_client = XunfeiASRClient(
        appid=xunfei_config['appid'],
        api_key=xunfei_config['api_key'],
        api_secret=xunfei_config['api_secret']
    )
    
    print("✅ 配置加载成功")
    print(f"   APPID: {xunfei_config['appid']}")
    print(f"   API Key: {xunfei_config['api_key'][:10]}...")
    
    # 测试1: 连接测试
    print("\n" + "-"*60)
    print("测试 1/2: WebSocket 连接")
    print("-"*60)
    
    try:
        print("正在连接...")
        await asr_client._connect()
        
        if asr_client.ws and asr_client.ws.state.name == "OPEN":
            print("✅ 连接成功！")
            await asr_client.close()
            print("✅ 连接已关闭")
        else:
            print("❌ 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {e}")
        return False
    
    # 等待一段时间
    print("\n⏳ 等待 5 秒...")
    await asyncio.sleep(5)
    
    # 测试2: 音频识别测试（使用静音音频）
    print("\n" + "-"*60)
    print("测试 2/2: 音频识别（静音音频）")
    print("-"*60)
    
    try:
        # 读取静音音频
        audio_path = "test_audio/silence_1s.wav"
        print(f"读取音频: {audio_path}")
        
        import wave
        with wave.open(audio_path, 'rb') as wav_file:
            audio_data = wav_file.readframes(wav_file.getnframes())
        
        print(f"音频大小: {len(audio_data)} 字节")
        print("\n开始识别...")
        
        result = await asr_client.transcribe(audio_data)
        
        print(f"✅ 识别完成")
        print(f"   结果: '{result}' (静音音频应为空)")
        
        return True
        
    except Exception as e:
        print(f"❌ 识别失败: {type(e).__name__}: {e}")
        return False


async def main():
    """主函数"""
    print("\n🚀 开始快速测试...\n")
    
    success = await quick_test()
    
    print("\n" + "="*60)
    if success:
        print("✅ 测试通过！ASR 功能正常工作")
        print("\n提示:")
        print("- 连接和识别都正常")
        print("- 可以使用 test_asr_audio.py 进行完整测试")
        print("- 真实语音请放到 test_audio/real/ 目录")
    else:
        print("❌ 测试失败")
        print("\n可能的原因:")
        print("1. 频繁测试触发限制（等待 30-60 分钟）")
        print("2. 网络问题（检查网络连接）")
        print("3. 配置问题（检查 config/api_keys.json）")
        print("\n诊断:")
        print("运行 diagnose_xunfei.py 获取详细信息")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
    
    print("\n✅ 完成！\n")
