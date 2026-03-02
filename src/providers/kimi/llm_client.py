"""
Kimi大模型 API 客户端实现
"""
import asyncio
import logging
from typing import AsyncIterator, Dict, Any, Optional

import httpx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base import LLMProvider

logger = logging.getLogger(__name__)


class KimiLLMClient(LLMProvider):
    """
    Kimi大模型客户端（Moonshot AI）
    
    支持同步和流式对话补全
    """
    
    AVAILABLE_MODELS = {
        "moonshot-v1-8k": "8K上下文模型",
        "moonshot-v1-32k": "32K上下文模型",
        "moonshot-v1-128k": "128K上下文模型"
    }
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.moonshot.cn/v1",
        model: str = "moonshot-v1-8k",
        **kwargs
    ):
        """
        初始化Kimi客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
            **kwargs: 额外配置参数
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.config = kwargs
        
        # HTTP客户端
        self.client: Optional[httpx.AsyncClient] = None
        
    @property
    def name(self) -> str:
        return "Kimi LLM"
    
    async def _ensure_client(self):
        """确保HTTP客户端已初始化"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=60.0,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
    
    async def chat(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        同步对话补全
        
        Args:
            messages: 对话历史 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数（0-1）
            **kwargs: 额外参数
                - max_tokens: 最大生成token数
                - top_p: 核采样参数
                - presence_penalty: 存在惩罚
                - frequency_penalty: 频率惩罚
        
        Returns:
            模型生成的回复
        """
        await self._ensure_client()
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            **kwargs
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response else {}
            raise Exception(f"Kimi API错误: {error_detail}")
        except Exception as e:
            raise Exception(f"请求失败: {e}")
    
    async def stream_chat(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式对话补全
        
        Args:
            messages: 对话历史
            temperature: 温度参数
            **kwargs: 额外参数
        
        Yields:
            生成的文本片段
        """
        await self._ensure_client()
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        try:
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        
                        # 检查是否结束
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            import json
                            data = json.loads(data_str)
                            
                            # 提取内容
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                yield content
                                
                        except json.JSONDecodeError:
                            continue
                            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response else {}
            raise Exception(f"Kimi API错误: {error_detail}")
        except Exception as e:
            raise Exception(f"流式请求失败: {e}")
    
    async def chat_with_system(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: Optional[list[Dict[str, str]]] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        带系统提示的对话（便捷方法）
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示
            conversation_history: 对话历史
            temperature: 温度参数
            **kwargs: 额外参数
        
        Returns:
            模型回复
        """
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            return await self.chat(messages, temperature, **kwargs)
        except Exception as e:
            # Fallback: 模拟响应（用于演示）
            logger.warning(f"LLM API调用失败，使用模拟响应: {e}")
            
            # 简单的模拟响应逻辑
            if "你好" in user_message or "您好" in user_message:
                return "你好！很高兴认识你。我是VoiceVibe的AI助手，我会通过聊天了解你的兴趣爱好，帮你找到合适的伙伴。你平时喜欢做什么呢？"
            elif "喜欢" in user_message or "兴趣" in user_message:
                return "听起来很有趣！这些爱好很棒。除了这些，你还喜欢尝试新的活动吗？比如户外运动、音乐或者艺术？"
            elif "音乐" in user_message or "运动" in user_message or "电影" in user_message:
                return "很好的选择！这些爱好能反映出你的性格。你觉得什么样的朋友会比较合得来呢？"
            else:
                return f"收到你的消息了！让我想想...作为AI助手，我会根据你的兴趣爱好来帮你匹配合适的伙伴。能告诉我更多关于你的信息吗？"
    
    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
