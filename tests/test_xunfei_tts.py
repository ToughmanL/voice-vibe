"""
测试科大讯飞TTS客户端
"""
import pytest
import base64
from unittest.mock import AsyncMock, patch

from src.providers.xunfei.tts_client import XunfeiTTSClient


class TestXunfeiTTSClient:
    """讯飞TTS客户端测试"""
    
    @pytest.fixture
    def tts_client(self):
        """创建TTS客户端实例"""
        return XunfeiTTSClient(
            appid="test_appid",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
    
    def test_init(self, tts_client):
        """测试初始化"""
        assert tts_client.appid == "test_appid"
        assert tts_client.api_key == "test_api_key"
        assert tts_client.api_secret == "test_api_secret"
        assert tts_client.ws is None
    
    def test_name_property(self, tts_client):
        """测试name属性"""
        assert tts_client.name == "Xunfei TTS"
    
    def test_voices_constant(self, tts_client):
        """测试预设音色"""
        assert "xiaoyan" in XunfeiTTSClient.VOICES
        assert len(XunfeiTTSClient.VOICES) > 0
    
    def test_generate_auth_url(self, tts_client):
        """测试鉴权URL生成"""
        url = tts_client._generate_auth_url()
        
        assert url.startswith("wss://ws-api.xfyun.cn/v2/tts?")
        assert "authorization=" in url
        assert "date=" in url
    
    @pytest.mark.asyncio
    async def test_synthesize_with_mock(self, tts_client):
        """测试同步合成（模拟）"""
        text = "你好，世界"
        
        # 模拟音频数据
        fake_audio = b'\x00\x00' * 16000
        fake_audio_base64 = base64.b64encode(fake_audio).decode('utf-8')
        
        # 模拟WebSocket响应
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(return_value=f'{{"code": 0, "data": {{"audio": "{fake_audio_base64}", "status": 2}}}}')
        mock_ws.send = AsyncMock()
        mock_ws.close = AsyncMock()
        
        with patch('websockets.connect', return_value=mock_ws):
            audio_data = await tts_client.synthesize(text, voice="xiaoyan")
            
            # 验证返回的是音频数据
            assert isinstance(audio_data, bytes)
            assert len(audio_data) > 0
    
    @pytest.mark.asyncio
    async def test_stream_synthesize_with_mock(self, tts_client):
        """测试流式合成（模拟）"""
        text = "测试流式合成"
        
        # 模拟音频片段
        audio_chunk1 = b'\x01\x00' * 8000
        audio_chunk2 = b'\x02\x00' * 8000
        
        responses = [
            f'{{"code": 0, "data": {{"audio": "{base64.b64encode(audio_chunk1).decode()}", "status": 1}}}}',
            f'{{"code": 0, "data": {{"audio": "{base64.b64encode(audio_chunk2).decode()}", "status": 2}}}}'
        ]
        
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=responses)
        mock_ws.send = AsyncMock()
        mock_ws.close = AsyncMock()
        
        chunks = []
        
        with patch('websockets.connect', return_value=mock_ws):
            async for chunk in tts_client.stream_synthesize(text):
                chunks.append(chunk)
            
            assert len(chunks) == 2
            assert chunks[0] == audio_chunk1
            assert chunks[1] == audio_chunk2
    
    @pytest.mark.asyncio
    async def test_synthesize_error_handling(self, tts_client):
        """测试错误处理"""
        text = "测试错误"
        
        # 模拟错误响应
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(return_value='{"code": 1001, "message": "Invalid parameter"}')
        mock_ws.send = AsyncMock()
        mock_ws.close = AsyncMock()
        
        with patch('websockets.connect', return_value=mock_ws):
            with pytest.raises(Exception) as exc_info:
                await tts_client.synthesize(text)
            
            assert "TTS错误" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
