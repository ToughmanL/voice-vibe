#!/usr/bin/env python3
"""
测试真实音频文件识别
"""
import asyncio
import sys
import wave
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from providers.xunfei.asr_client import XunfeiASRClient
from config_loader import ConfigLoader


async def test_audio_file(audio_path):
    """测试音频文件识别"""
    print("="*60)
    print("科大讯飞 ASR - 真实音频测试")
    print("="*60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"文件: {audio_path}")
    
    # 检查文件
    if not Path(audio_path).exists():
        print(f"\n❌ 文件不存在: {audio_path}")
        return
    
    # 读取音频信息
    print("\n📊 音频信息:")
    with wave.open(audio_path, 'rb') as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        num_frames = wav.getnframes()
        duration = num_frames / framerate
        
        print(f"   声道数: {channels}")
        print(f"   采样位数: {sample_width * 8} bit")
        print(f"   采样率: {framerate} Hz")
        print(f"   时长: {duration:.2f} 秒")
        
        # 读取音频数据
        audio_data = wav.readframes(num_frames)
        print(f"   数据大小: {len(audio_data)} 字节")
    
    # 加载配置
    print("\n⚙️  加载配置...")
    config_loader = ConfigLoader()
    xunfei_config = config_loader.xunfei_asr
    
    # 创建 ASR 客户端
    asr_client = XunfeiASRClient(
        appid=xunfei_config['appid'],
        api_key=xunfei_config['api_key'],
        api_secret=xunfei_config['api_secret']
    )
    
    print("✅ ASR 客户端创建成功")
    
    # 开始识别
    print("\n🎯 开始语音识别...")
    print("   (这可能需要几秒钟)")
    
    try:
        start_time = datetime.now()
        
        result = await asr_client.transcribe(
            audio_data,
            sample_rate=framerate,
            language="zh_cn",
            domain="iat",
            accent="mandarin"
        )
        
        end_time = datetime.now()
        duration_sec = (end_time - start_time).total_seconds()
        
        print(f"\n✅ 识别完成！")
        print(f"   耗时: {duration_sec:.2f} 秒")
        print(f"\n📝 识别结果:")
        print(f"   {result}")
        
        if not result:
            print("\n⚠️  识别结果为空")
            print("   可能原因:")
            print("   1. 音频中无语音内容")
            print("   2. 音量太小")
            print("   3. 背景噪音太大")
        else:
            print(f"\n✅ 识别成功！共 {len(result)} 个字符")
        
        # 保存结果
        result_file = "test_result.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(f"音频文件: {audio_path}\n")
            f.write(f"识别时间: {datetime.now().isoformat()}\n")
            f.write(f"耗时: {duration_sec:.2f} 秒\n")
            f.write(f"识别结果: {result}\n")
        
        print(f"\n📄 结果已保存到: {result_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 识别失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # 音频文件路径
    audio_file = "/Users/jack/Downloads/test.wav"
    
    print("\n🚀 开始测试...\n")
    
    try:
        result = asyncio.run(test_audio_file(audio_file))
        
        if result is not None:
            print("\n" + "="*60)
            print("✅ 测试完成")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ 测试失败")
            print("="*60)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ 程序结束\n")
