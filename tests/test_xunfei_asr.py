"""
测试科大讯飞ASR客户端
"""
import pytest
import asyncio
import base64
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from src.providers.xunfei.asr_client import XunfeiASRClient


class TestXunfeiASRClient:
    """讯飞ASR客户端测试"""
    
    @pytest.fixture
    def asr_client(self):
        """创建ASR客户端实例"""
        return XunfeiASRClient(
            appid="test_appid",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
    
    def test_init(self, asr_client):
        """测试初始化"""
        assert asr_client.appid == "test_appid"
        assert asr_client.api_key == "test_api_key"
        assert asr_client.api_secret == "test_api_secret"
        assert asr_client.ws is None
    
    def test_name_property(self, asr_client):
        """测试name属性"""
        assert asr_client.name == "Xunfei ASR"
    
    def test_generate_auth_url(self, asr_client):
        """测试鉴权URL生成"""
        url = asr_client._generate_auth_url()
        
        # 验证URL格式
        assert url.startswith("wss://ws-api.xfyun.cn/v2/iat?")
        assert "authorization=" in url
        assert "date=" in url
        assert "host=" in url
    
    @pytest.mark.asyncio
    async def test_transcribe_with_mock(self, asr_client):
        """测试同步识别（模拟WebSocket）"""
        # 模拟音频数据（16位PCM，16kHz，1秒）
        audio_data = b'\x00\x00' * 16000
        
        # 模拟WebSocket响应
        mock_ws = AsyncMock()
        mock_ws.closed = False
        
        # 模拟接收消息
        messages = [
            '{"action": "result", "data": {"result": {"ws": [{"cw": [{"w": "你好"}]}]}}}',
            '{"action": "finished"}'
        ]
        mock_ws.recv = AsyncMock(side_effect=messages)
        mock_ws.send = AsyncMock()
        mock_ws.close = AsyncMock()
        
        # 注入mock WebSocket
        with patch('websockets.connect', return_value=mock_ws):
            result = await asr_client.transcribe(audio_data)
            
            # 验证结果
            assert result == "你好"
            
            # 验证WebSocket被调用
            assert mock_ws.send.called
    
    @pytest.mark.asyncio
    async def test_stream_transcribe_with_mock(self, asr_client):
        """测试流式识别（模拟）"""
        # 模拟音频流
        async def audio_stream():
            yield b'\x00\x00' * 8000  # 0.5秒音频
            yield b'\x00\x00' * 8000  # 0.5秒音频
        
        # 模拟WebSocket
        mock_ws = AsyncMock()
        mock_ws.closed = False
        messages = [
            '{"action": "result", "data": {"result": {"ws": [{"cw": [{"w": "测试"}]}]}}}',
            '{"action": "finished"}'
        ]
        mock_ws.recv = AsyncMock(side_effect=messages)
        mock_ws.send = AsyncMock()
        mock_ws.close = AsyncMock()
        
        results = []
        
        with patch('websockets.connect', return_value=mock_ws):
            async for text in asr_client.stream_transcribe(audio_stream()):
                results.append(text)
            
            assert "测试" in results
    
    @pytest.mark.asyncio
    async def test_close(self, asr_client):
        """测试关闭连接"""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        asr_client.ws = mock_ws
        
        await asr_client.close()
        
        mock_ws.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
