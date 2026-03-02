"""
核心抽象基类 - 定义所有服务的接口规范
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional


class ASRProvider(ABC):
    """语音识别服务抽象基类"""
    
    @abstractmethod
    async def transcribe(
        self, 
        audio_data: bytes,
        sample_rate: int = 16000,
        **kwargs
    ) -> str:
        """
        将音频数据转换为文本
        
        Args:
            audio_data: 音频二进制数据
            sample_rate: 采样率（默认16000）
            **kwargs: 额外参数
        
        Returns:
            识别的文本结果
        """
        pass
    
    @abstractmethod
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
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """服务名称"""
        pass


class TTSProvider(ABC):
    """语音合成服务抽象基类"""
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        将文本转换为语音
        
        Args:
            text: 要合成的文本
            voice: 音色ID（可选）
            **kwargs: 额外参数（如语速、音调等）
        
        Returns:
            音频二进制数据
        """
        pass
    
    @abstractmethod
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
            voice: 音色ID
            **kwargs: 额外参数
        
        Yields:
            音频数据片段
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """服务名称"""
        pass


class LLMProvider(ABC):
    """大语言模型服务抽象基类"""
    
    @abstractmethod
    async def chat(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        对话补全
        
        Args:
            messages: 对话历史 [{"role": "user/assistant", "content": "..."}]
            temperature: 温度参数
            **kwargs: 额外参数
        
        Returns:
            模型生成的回复
        """
        pass
    
    @abstractmethod
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
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """服务名称"""
        pass


class MatchingEngine(ABC):
    """匹配引擎抽象基类"""
    
    @abstractmethod
    async def analyze_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析用户画像，提取特征
        
        Args:
            profile: 用户信息（年龄、兴趣、语音特征等）
        
        Returns:
            特征向量或结构化特征
        """
        pass
    
    @abstractmethod
    async def find_matches(
        self,
        user_features: Dict[str, Any],
        candidates: list[Dict[str, Any]],
        top_k: int = 5
    ) -> list[Dict[str, Any]]:
        """
        找到最匹配的候选人
        
        Args:
            user_features: 当前用户的特征
            candidates: 候选人列表及其特征
            top_k: 返回前K个最佳匹配
        
        Returns:
            匹配结果列表，包含相似度分数
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """引擎名称"""
        pass
