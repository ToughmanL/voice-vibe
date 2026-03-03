#!/usr/bin/env python3
"""
科大讯飞 ASR 音频测试工具
使用本地音频文件进行完整的端到端测试
"""
import asyncio
import json
import sys
import os
import wave
import time
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from providers.xunfei.asr_client import XunfeiASRClient
from config_loader import ConfigLoader


class ASRTester:
    """ASR 测试器"""
    
    def __init__(self, config_path=None):
        """初始化测试器"""
        # 加载配置
        self.config_loader = ConfigLoader(config_path)
        xunfei_config = self.config_loader.xunfei_asr
        
        # 创建ASR客户端
        self.asr_client = XunfeiASRClient(
            appid=xunfei_config['appid'],
            api_key=xunfei_config['api_key'],
            api_secret=xunfei_config['api_secret']
        )
        
        # 测试结果
        self.test_results = []
        
        # 频率控制
        self.last_request_time = 0
        self.min_interval = 5  # 最小请求间隔（秒）
    
    def read_wav_file(self, wav_path):
        """读取WAV音频文件"""
        print(f"\n📂 读取音频文件: {wav_path}")
        
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"音频文件不存在: {wav_path}")
        
        with wave.open(wav_path, 'rb') as wav_file:
            # 检查音频格式
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            num_frames = wav_file.getnframes()
            
            print(f"   声道数: {channels}")
            print(f"   采样位数: {sample_width * 8} bit")
            print(f"   采样率: {framerate} Hz")
            print(f"   时长: {num_frames / framerate:.2f} 秒")
            
            # 验证格式
            if channels != 1:
                raise ValueError("音频必须是单声道")
            if sample_width != 2:
                raise ValueError("音频必须是16位")
            if framerate not in [8000, 16000]:
                raise ValueError("采样率必须是 8000 或 16000 Hz")
            
            # 读取音频数据
            audio_data = wav_file.readframes(num_frames)
            
            print(f"   数据大小: {len(audio_data)} 字节")
            
            return audio_data, framerate
    
    async def wait_for_rate_limit(self):
        """等待频率限制"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"\n⏳ 等待 {wait_time:.1f} 秒（避免频率限制）...")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def test_audio_file(self, audio_path, description=""):
        """测试单个音频文件"""
        print("\n" + "="*60)
        print(f"测试: {description or os.path.basename(audio_path)}")
        print("="*60)
        
        result = {
            "file": audio_path,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "text": "",
            "error": None,
            "duration": 0
        }
        
        try:
            # 读取音频
            audio_data, sample_rate = self.read_wav_file(audio_path)
            
            # 等待频率限制
            await self.wait_for_rate_limit()
            
            # 开始识别
            print(f"\n🎯 开始语音识别...")
            start_time = time.time()
            
            text = await self.asr_client.transcribe(
                audio_data,
                sample_rate=sample_rate,
                language="zh_cn",
                domain="iat",
                accent="mandarin"
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            result["success"] = True
            result["text"] = text
            result["duration"] = duration
            
            print(f"\n✅ 识别成功！")
            print(f"   耗时: {duration:.2f} 秒")
            print(f"   结果: '{text}'")
            
            if not text:
                print(f"   ℹ️  空结果（可能是静音音频）")
            
        except FileNotFoundError as e:
            result["error"] = str(e)
            print(f"\n❌ 文件错误: {e}")
            
        except Exception as e:
            result["error"] = f"{type(e).__name__}: {e}"
            print(f"\n❌ 识别失败: {type(e).__name__}: {e}")
            
            import traceback
            print("\n详细错误:")
            traceback.print_exc()
        
        self.test_results.append(result)
        return result
    
    async def test_connection_only(self):
        """仅测试连接（不发送音频）"""
        print("\n" + "="*60)
        print("测试: WebSocket 连接")
        print("="*60)
        
        result = {
            "test": "connection",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None
        }
        
        try:
            print(f"\n🔗 建立连接...")
            
            # 等待频率限制
            await self.wait_for_rate_limit()
            
            # 测试连接
            await self.asr_client._connect()
            
            if self.asr_client.ws and not self.asr_client.ws.closed:
                print(f"✅ 连接成功！")
                result["success"] = True
                
                # 关闭连接
                await self.asr_client.close()
                print(f"✅ 连接已关闭")
            else:
                print(f"❌ 连接失败")
                result["error"] = "连接未建立"
                
        except Exception as e:
            result["error"] = f"{type(e).__name__}: {e}"
            print(f"❌ 连接失败: {type(e).__name__}: {e}")
            
            import traceback
            print("\n详细错误:")
            traceback.print_exc()
        
        self.test_results.append(result)
        return result
    
    def print_summary(self):
        """打印测试汇总"""
        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)
        
        total = len(self.test_results)
        success = sum(1 for r in self.test_results if r["success"])
        failed = total - success
        
        print(f"\n总测试数: {total}")
        print(f"✅ 成功: {success}")
        print(f"❌ 失败: {failed}")
        
        if total > 0:
            print(f"\n成功率: {success/total*100:.1f}%")
        
        # 详细结果
        print("\n详细结果:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            desc = result.get("description") or result.get("file") or result.get("test", "未知")
            print(f"\n{i}. {status} {desc}")
            
            if result["success"]:
                if "text" in result:
                    print(f"   识别结果: '{result['text']}'")
                if "duration" in result:
                    print(f"   耗时: {result['duration']:.2f}秒")
            else:
                print(f"   错误: {result['error']}")
        
        print("\n" + "="*60)
    
    def save_results(self, output_file="test_results.json"):
        """保存测试结果到文件"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "success_count": sum(1 for r in self.test_results if r["success"]),
            "results": self.test_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试结果已保存到: {output_file}")


async def main():
    """主测试流程"""
    print("="*60)
    print("科大讯飞 ASR 音频测试工具")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试器
    tester = ASRTester()
    
    # 测试1: 连接测试（可选，跳过以避免频繁连接）
    print("\n\n⚠️  跳过单独的连接测试（避免频繁连接）")
    print("将在音频测试时自动建立连接")
    
    # 测试音频目录
    audio_dir = "test_audio"
    
    if not os.path.exists(audio_dir):
        print(f"\n❌ 测试音频目录不存在: {audio_dir}")
        print("\n请先运行以下命令生成测试音频:")
        print("  python3 generate_test_audio.py")
        return
    
    # 测试2: 静音音频
    silence_files = [
        ("test_audio/silence_1s.wav", "静音音频（1秒）"),
        ("test_audio/silence_3s.wav", "静音音频（3秒）")
    ]
    
    for audio_path, desc in silence_files:
        if os.path.exists(audio_path):
            await tester.test_audio_file(audio_path, desc)
            # 增加等待时间，避免频率限制
            print(f"\n⏳ 等待 10 秒...")
            await asyncio.sleep(10)
        else:
            print(f"\n⚠️  跳过（文件不存在）: {audio_path}")
    
    # 测试3: 单音音频（可选）
    tone_files = [
        ("test_audio/tone_440hz_2s.wav", "单音音频（440Hz）"),
        ("test_audio/tone_880hz_2s.wav", "单音音频（880Hz）")
    ]
    
    print("\n\n⚠️  跳过单音音频测试（无实际语音）")
    print("如需测试，请取消注释以下代码:")
    print("""
for audio_path, desc in tone_files:
    if os.path.exists(audio_path):
        await tester.test_audio_file(audio_path, desc)
        await asyncio.sleep(10)
    """)
    
    # 测试4: 真实语音（如果有）
    real_audio_dir = "test_audio/real"
    if os.path.exists(real_audio_dir):
        print(f"\n\n🔍 检测到真实语音目录: {real_audio_dir}")
        
        for filename in os.listdir(real_audio_dir):
            if filename.endswith('.wav'):
                audio_path = os.path.join(real_audio_dir, filename)
                await tester.test_audio_file(audio_path, f"真实语音: {filename}")
                print(f"\n⏳ 等待 10 秒...")
                await asyncio.sleep(10)
    
    # 打印汇总
    tester.print_summary()
    
    # 保存结果
    tester.save_results()


if __name__ == "__main__":
    print("\n🚀 开始测试...\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ 测试完成！\n")
