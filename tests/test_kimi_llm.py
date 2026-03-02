"""
测试Kimi LLM客户端
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from src.providers.kimi.llm_client import KimiLLMClient


class TestKimiLLMClient:
    """Kimi LLM客户端测试"""
    
    @pytest.fixture
    def llm_client(self):
        """创建LLM客户端实例"""
        return KimiLLMClient(
            api_key="test_api_key",
            base_url="https://api.moonshot.cn/v1",
            model="moonshot-v1-8k"
        )
    
    def test_init(self, llm_client):
        """测试初始化"""
        assert llm_client.api_key == "test_api_key"
        assert llm_client.base_url == "https://api.moonshot.cn/v1"
        assert llm_client.model == "moonshot-v1-8k"
        assert llm_client.client is None
    
    def test_name_property(self, llm_client):
        """测试name属性"""
        assert llm_client.name == "Kimi LLM"
    
    def test_available_models(self, llm_client):
        """测试可用模型列表"""
        assert "moonshot-v1-8k" in KimiLLMClient.AVAILABLE_MODELS
        assert "moonshot-v1-32k" in KimiLLMClient.AVAILABLE_MODELS
    
    @pytest.mark.asyncio
    async def test_chat_with_mock(self, llm_client):
        """测试同步对话（模拟HTTP）"""
        messages = [
            {"role": "user", "content": "你好"}
        ]
        
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "你好！有什么可以帮助你的吗？"
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch.object(llm_client, '_ensure_client'):
            llm_client.client = mock_client
            
            result = await llm_client.chat(messages, temperature=0.7)
            
            # 验证结果
            assert "你好" in result
            
            # 验证HTTP调用
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            # 验证URL和payload
            assert call_args[0][0].endswith("/chat/completions")
            assert call_args[1]["json"]["model"] == "moonshot-v1-8k"
            assert call_args[1]["json"]["messages"] == messages
    
    @pytest.mark.asyncio
    async def test_stream_chat_with_mock(self, llm_client):
        """测试流式对话（模拟）"""
        messages = [
            {"role": "user", "content": "讲个故事"}
        ]
        
        # 模拟流式响应
        stream_lines = [
            'data: {"choices":[{"delta":{"content":"很"}}]}'.encode('utf-8'),
            'data: {"choices":[{"delta":{"content":"久"}}]}'.encode('utf-8'),
            'data: {"choices":[{"delta":{"content":"以前..."}}]}'.encode('utf-8'),
            b'data: [DONE]'
        ]
        
        # 创建异步迭代器
        async def async_iter():
            for line in stream_lines:
                yield line
        
        mock_response = MagicMock()
        mock_response.aiter_lines = async_iter
        mock_response.raise_for_status = MagicMock()
        
        # 创建上下文管理器
        async_context = AsyncMock()
        async_context.__aenter__ = AsyncMock(return_value=mock_response)
        async_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = AsyncMock()
        mock_client.stream = MagicMock(return_value=async_context)
        
        with patch.object(llm_client, '_ensure_client'):
            llm_client.client = mock_client
            
            chunks = []
            async for chunk in llm_client.stream_chat(messages):
                chunks.append(chunk)
            
            # 验证结果
            assert len(chunks) == 3
            assert "".join(chunks) == "很久以前..."
    
    @pytest.mark.asyncio
    async def test_chat_with_system(self, llm_client):
        """测试带系统提示的对话"""
        user_message = "今天天气怎么样？"
        system_prompt = "你是一个天气助手"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "抱歉，我无法获取实时天气信息。"
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch.object(llm_client, '_ensure_client'):
            llm_client.client = mock_client
            
            result = await llm_client.chat_with_system(
                user_message=user_message,
                system_prompt=system_prompt
            )
            
            # 验证系统提示被添加
            call_args = mock_client.post.call_args
            sent_messages = call_args[1]["json"]["messages"]
            
            assert sent_messages[0]["role"] == "system"
            assert sent_messages[0]["content"] == system_prompt
            assert sent_messages[-1]["role"] == "user"
            assert sent_messages[-1]["content"] == user_message
    
    @pytest.mark.asyncio
    async def test_error_handling(self, llm_client):
        """测试错误处理"""
        messages = [{"role": "user", "content": "测试"}]
        
        # 模拟HTTP错误
        from httpx import HTTPStatusError
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Invalid API key"}
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(
            side_effect=HTTPStatusError(
                message="401 Unauthorized",
                request=MagicMock(),
                response=mock_response
            )
        )
        
        with patch.object(llm_client, '_ensure_client'):
            llm_client.client = mock_client
            
            with pytest.raises(Exception) as exc_info:
                await llm_client.chat(messages)
            
            assert "Kimi API错误" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
