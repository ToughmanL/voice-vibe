"""
科大讯飞语音合成 WebSocket 客户端实现
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

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base import TTSProvider


class XunfeiTTSClient(TTSProvider):
    """
    科大讯飞语音合成客户端
    
    支持流式语音合成，基于WebSocket协议
    """
    
    # 预设音色列表
    VOICES = {
        "xiaoyan": "小燕（亲和女声）",
        "aisjiuxu": "许久（亲切男声）",
        "aisxping": "小萍（温柔女声）",
        "aisjinger": "小婧（柔美女声）",
        "aisbabyxu": "许小宝（童声）",
    }
    
    def __init__(
        self,
        appid: str,
        api_key: str,
        api_secret: str,
        **kwargs
    ):
        """
        初始化讯飞TTS客户端
        
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
        return "Xunfei TTS"
    
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
        signature_origin = f"host: ws-api.xfyun.cn\ndate: {date}\nGET /v2/tts HTTP/1.1"
        
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
        
        return f"wss://ws-api.xfyun.cn/v2/tts?{urlencode(params)}"
    
    async def _connect(self):
        """建立WebSocket连接"""
        if self.ws is None or self.ws.state.name != "OPEN":
            url = self._generate_auth_url()
            self.ws = await websockets.connect(
                url,
                open_timeout=30,
                close_timeout=10
            )
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        同步语音合成（一次性返回完整音频）
        
        Args:
            text: 要合成的文本
            voice: 音色ID（默认小燕）
            **kwargs: 额外参数（如语速、音调等）
        
        Returns:
            音频数据（PCM格式）
        """
        audio_chunks = []
        async for chunk in self.stream_synthesize(text, voice, **kwargs):
            audio_chunks.append(chunk)
        return b''.join(audio_chunks)
    
    async def stream_synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[bytes]:
        """
        流式语音合成
        
        Args:
            text: 要合成的文本
            voice: 音色ID（默认xiaoyan）
            **kwargs: 额外参数
                - speed: 语速（0-100，默认50）
                - volume: 音量（0-100，默认50）
                - pitch: 音高（0-100，默认50）
        
        Yields:
            音频数据片段（PCM格式）
        """
        await self._connect()
        
        try:
            # 构建请求
            request_data = {
                "common": {
                    "app_id": self.appid
                },
                "business": {
                    "aue": "raw",  # 原始PCM
                    "auf": "audio/L16;rate=16000",  # 16k采样率
                    "vcn": voice or kwargs.get("vcn", "xiaoyan"),  # 音色
                    "speed": kwargs.get("speed", 50),  # 语速
                    "volume": kwargs.get("volume", 50),  # 音量
                    "pitch": kwargs.get("pitch", 50),  # 音高
                    "bgs": kwargs.get("bgs", 0),  # 背景音
                    "tte": kwargs.get("tte", "UTF8")  # 文本编码
                },
                "data": {
                    "status": 2,  # 一次性传输
                    "text": base64.b64encode(text.encode('utf-8')).decode('utf-8')
                }
            }
            
            # 发送请求
            await self.ws.send(json.dumps(request_data))
            
            # 接收音频数据
            while True:
                try:
                    message = await asyncio.wait_for(
                        self.ws.recv(),
                        timeout=30.0
                    )
                    data = json.loads(message)
                    
                    # 检查错误
                    if data.get("code") != 0:
                        error_msg = data.get("message", "未知错误")
                        raise Exception(f"TTS错误 [{data.get('code')}]: {error_msg}")
                    
                    # 提取音频数据
                    if "data" in data and "audio" in data["data"]:
                        audio_base64 = data["data"]["audio"]
                        audio_bytes = base64.b64decode(audio_base64)
                        yield audio_bytes
                    
                    # 检查是否结束
                    if data["data"].get("status") == 2:
                        break
                        
                except asyncio.TimeoutError:
                    raise TimeoutError("TTS合成超时")
                except json.JSONDecodeError as e:
                    raise Exception(f"JSON解析错误: {e}")
                    
        except Exception as e:
            print(f"TTS合成错误: {e}")
            raise
        finally:
            if self.ws and self.ws.state.name == "OPEN":
                await self.ws.close()
    
    async def close(self):
        """关闭连接"""
        if self.ws and not self.ws.closed:
            await self.ws.close()
