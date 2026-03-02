"""
科大讯飞语音识别 WebSocket 客户端实现
"""
import asyncio
import hmac
import base64
import json
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlencode
from typing import AsyncIterator, Optional

import websockets

from ...core.base import ASRProvider


class XunfeiASRClient(ASRProvider):
    """
    科大讯飞语音识别客户端
    
    支持实时流式语音识别，基于WebSocket协议
    """
    
    def __init__(
        self,
        appid: str,
        api_key: str,
        api_secret: str,
        **kwargs
    ):
        """
        初始化讯飞ASR客户端
        
        Args:
            appid: 应用ID
            api_key: API密钥
            api_secret: API密钥密文
            **kwargs: 额外配置参数
        """
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.config = kwargs
        
        # WebSocket连接
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        
    @property
    def name(self) -> str:
        return "Xunfei ASR"
    
    def _generate_auth_url(self) -> str:
        """
        生成鉴权后的WebSocket URL
        
        Returns:
            带鉴权参数的WebSocket URL
        """
        # 生成RFC1123格式的时间戳
        now = datetime.now(timezone.utc)
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接签名原文
        signature_origin = f"host: ws-api.xfyun.cn\ndate: {date}\nGET /v2/iat HTTP/1.1"
        
        # 使用HMAC-SHA256计算签名
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        # 拼接authorization原文
        authorization_origin = (
            f'api_key="{self.api_key}", '
            f'algorithm="hmac-sha256", '
            f'headers="host date request-line", '
            f'signature="{signature}"'
        )
        
        # Base64编码
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')
        ).decode(encoding='utf-8')
        
        # 构建完整URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        
        return f"wss://ws-api.xfyun.cn/v2/iat?{urlencode(params)}"
    
    async def _connect(self):
        """建立WebSocket连接"""
        if self.ws is None or self.ws.closed:
            url = self._generate_auth_url()
            self.ws = await websockets.connect(url)
    
    async def transcribe(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
        **kwargs
    ) -> str:
        """
        同步语音识别（一次性传输）
        
        Args:
            audio_data: 音频数据（PCM格式）
            sample_rate: 采样率
            **kwargs: 额外参数
        
        Returns:
            识别文本
        """
        result = ""
        async for text in self.stream_transcribe(
            self._async_iter(audio_data),
            sample_rate,
            **kwargs
        ):
            result += text
        return result
    
    async def stream_transcribe(
        self,
        audio_stream: AsyncIterator[bytes],
        sample_rate: int = 16000,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式语音识别
        
        Args:
            audio_stream: 音频数据流
            sample_rate: 采样率
            **kwargs: 额外参数
        
        Yields:
            识别的文本片段
        """
        await self._connect()
        
        try:
            # 接收结果的协程
            async def receive_results():
                results = []
                while True:
                    try:
                        message = await asyncio.wait_for(
                            self.ws.recv(),
                            timeout=30.0
                        )
                        data = json.loads(message)
                        
                        if data.get("action") == "result":
                            # 解析识别结果
                            data_json = data.get("data", {})
                            result_json = data_json.get("result", {})
                            
                            # 提取文本
                            ws_list = result_json.get("ws", [])
                            text = "".join(
                                w.get("cw", [{}])[0].get("w", "")
                                for w in ws_list
                            )
                            
                            if text:
                                results.append(text)
                        
                        # 检查是否结束
                        if data.get("action") == "finished":
                            break
                            
                    except asyncio.TimeoutError:
                        break
                    except Exception as e:
                        print(f"接收结果错误: {e}")
                        break
                
                return results
            
            # 启动接收协程
            receive_task = asyncio.create_task(receive_results())
            
            # 发送音频数据
            frame_size = 1280  # 40ms @ 16kHz 16bit
            frame_index = 0
            
            async for chunk in audio_stream:
                # 将音频数据分帧
                for i in range(0, len(chunk), frame_size):
                    frame = chunk[i:i+frame_size]
                    
                    # Base64编码音频
                    audio_base64 = base64.b64encode(frame).decode('utf-8')
                    
                    # 构建请求帧
                    frame_data = {
                        "common": {
                            "app_id": self.appid
                        },
                        "business": {
                            "language": kwargs.get("language", "zh_cn"),
                            "domain": kwargs.get("domain", "iat"),
                            "accent": kwargs.get("accent", "mandarin"),
                            "vad_eos": kwargs.get("vad_eos", 2000),
                            "dwa": kwargs.get("dwa", "wpgs")  # 动态修正
                        },
                        "data": {
                            "status": 1,  # 数据帧
                            "format": "audio/L16;rate=16000",
                            "encoding": "raw",
                            "audio": audio_base64
                        }
                    }
                    
                    # 第一帧
                    if frame_index == 0:
                        frame_data["data"]["status"] = 0
                    
                    await self.ws.send(json.dumps(frame_data))
                    frame_index += 1
                    
                    # 控制发送速率
                    await asyncio.sleep(0.04)  # 40ms
            
            # 发送结束帧
            end_frame = {
                "data": {
                    "status": 2,  # 结束帧
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw",
                    "audio": ""
                }
            }
            await self.ws.send(json.dumps(end_frame))
            
            # 等待接收完成
            results = await receive_task
            
            # 输出结果
            for text in results:
                yield text
                
        except Exception as e:
            print(f"流式识别错误: {e}")
            raise
        finally:
            if self.ws and not self.ws.closed:
                await self.ws.close()
    
    @staticmethod
    def _async_iter(data: bytes) -> AsyncIterator[bytes]:
        """将字节转换为异步迭代器"""
        async def iterator():
            yield data
        return iterator()
    
    async def close(self):
        """关闭连接"""
        if self.ws and not self.ws.closed:
            await self.ws.close()
