#!/usr/bin/env python3
"""
生成测试音频文件
用于科大讯飞 ASR 测试
"""
import wave
import struct
import math
import os

def generate_silence(filename, duration_sec=1, sample_rate=16000):
    """生成静音音频文件"""
    print(f"生成静音音频: {filename} ({duration_sec}秒)")
    
    num_samples = int(sample_rate * duration_sec)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16bit
        wav_file.setframerate(sample_rate)
        
        # 写入静音数据（全0）
        for _ in range(num_samples):
            wav_file.writeframes(struct.pack('<h', 0))
    
    print(f"✅ 已生成: {filename} ({os.path.getsize(filename)} 字节)")

def generate_tone(filename, frequency=440, duration_sec=2, sample_rate=16000, amplitude=0.3):
    """生成单音音频文件（用于测试音频传输，不是用于语音识别）"""
    print(f"生成单音音频: {filename} ({frequency}Hz, {duration_sec}秒)")
    
    num_samples = int(sample_rate * duration_sec)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16bit
        wav_file.setframerate(sample_rate)
        
        # 生成正弦波
        for i in range(num_samples):
            t = i / sample_rate
            value = amplitude * math.sin(2 * math.pi * frequency * t)
            sample = int(value * 32767)
            wav_file.writeframes(struct.pack('<h', sample))
    
    print(f"✅ 已生成: {filename} ({os.path.getsize(filename)} 字节)")

def main():
    """生成测试音频文件"""
    print("="*60)
    print("生成测试音频文件")
    print("="*60)
    
    # 创建测试音频目录
    audio_dir = "test_audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    print("\n📁 测试音频目录:", os.path.abspath(audio_dir))
    
    # 生成不同类型的测试音频
    print("\n生成测试音频文件...")
    
    # 1. 静音音频（1秒）
    generate_silence(f"{audio_dir}/silence_1s.wav", duration_sec=1)
    
    # 2. 静音音频（3秒）
    generate_silence(f"{audio_dir}/silence_3s.wav", duration_sec=3)
    
    # 3. 单音音频（440Hz，2秒）
    generate_tone(f"{audio_dir}/tone_440hz_2s.wav", frequency=440, duration_sec=2)
    
    # 4. 单音音频（880Hz，2秒）
    generate_tone(f"{audio_dir}/tone_880hz_2s.wav", frequency=880, duration_sec=2)
    
    print("\n" + "="*60)
    print("音频文件生成完成！")
    print("="*60)
    
    print("\n⚠️  注意：")
    print("1. 静音音频：用于测试连接和音频传输，识别结果应为空")
    print("2. 单音音频：用于测试音频编码，识别结果可能为空或乱码")
    print("3. 真实语音测试：请使用录音设备录制真实语音")
    
    print("\n💡 提示：")
    print("要测试真实语音识别，请：")
    print("1. 使用录音软件录制一段语音（16kHz, 16bit, 单声道）")
    print("2. 保存为 WAV 格式到 test_audio/ 目录")
    print("3. 使用 test_asr_audio.py 进行测试")

if __name__ == "__main__":
    main()
