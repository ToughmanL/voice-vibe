#!/usr/bin/env python3
"""
音频文件分析工具
检查音频文件的内容和质量
"""
import wave
import struct
import sys

def analyze_audio(audio_path):
    """分析音频文件"""
    print("="*60)
    print("音频文件分析")
    print("="*60)
    print(f"文件: {audio_path}\n")
    
    with wave.open(audio_path, 'rb') as wav:
        # 基本信息
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        num_frames = wav.getnframes()
        duration = num_frames / framerate
        
        print("📊 基本信息:")
        print(f"   声道数: {channels}")
        print(f"   采样位数: {sample_width * 8} bit")
        print(f"   采样率: {framerate} Hz")
        print(f"   帧数: {num_frames}")
        print(f"   时长: {duration:.2f} 秒")
        
        # 读取所有音频数据
        audio_data = wav.readframes(num_frames)
        
        # 解析样本值
        if sample_width == 2:  # 16-bit
            samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data)
            
            # 统计分析
            max_val = max(samples)
            min_val = min(samples)
            avg_val = sum(samples) / len(samples)
            
            # 计算RMS（均方根）
            sum_sq = sum(s**2 for s in samples)
            rms = (sum_sq / len(samples)) ** 0.5
            
            # 计算分贝值
            if rms > 0:
                db = 20 * (2.303 * (rms / 32767.0)) / 2.303  # 近似计算
                db = 20 * (rms / 32767.0)
            else:
                db = -float('inf')
            
            print("\n📈 音频分析:")
            print(f"   样本数: {len(samples)}")
            print(f"   最大值: {max_val} ({max_val/32767*100:.1f}%)")
            print(f"   最小值: {min_val} ({min_val/32767*100:.1f}%)")
            print(f"   平均值: {avg_val:.2f}")
            print(f"   RMS 值: {rms:.2f}")
            print(f"   音量: {db:.2f} dB (满刻度为 0 dB)")
            
            # 检测静音
            silence_threshold = 100  # 静音阈值
            silent_samples = sum(1 for s in samples if abs(s) < silence_threshold)
            silent_ratio = silent_samples / len(samples) * 100
            
            print(f"\n🔇 静音分析:")
            print(f"   静音样本: {silent_samples} / {len(samples)}")
            print(f"   静音比例: {silent_ratio:.1f}%")
            
            # 判断音频质量
            print("\n✅ 质量评估:")
            if rms < 100:
                print("   ⚠️  音量过低 - 几乎为静音")
            elif rms < 1000:
                print("   ⚠️  音量较低 - 可能影响识别")
            elif rms < 10000:
                print("   ✅ 音量正常")
            else:
                print("   ✅ 音量良好")
            
            if silent_ratio > 90:
                print("   ⚠️  大部分为静音")
            elif silent_ratio > 50:
                print("   ⚠️  静音较多")
            else:
                print("   ✅ 语音内容充足")
            
            # 检测峰值
            peak_threshold = 30000
            peaks = sum(1 for s in samples if abs(s) > peak_threshold)
            if peaks > 0:
                print(f"   ✅ 检测到 {peaks} 个峰值点")
            
            # 建议操作
            print("\n💡 建议:")
            if rms < 100:
                print("   - 这个音频几乎是静音的")
                print("   - 请检查录音是否成功")
                print("   - 可能需要重新录制")
            elif silent_ratio > 80:
                print("   - 音频中静音部分太多")
                print("   - 建议裁剪掉静音部分")
            else:
                print("   - 音频质量良好")
                print("   - 可以用于语音识别")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = "/Users/jack/Downloads/test.wav"
    
    try:
        analyze_audio(audio_file)
    except FileNotFoundError:
        print(f"❌ 文件不存在: {audio_file}")
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
