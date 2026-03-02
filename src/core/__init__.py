"""
核心模块 - 定义抽象接口
"""
from .base import ASRProvider, TTSProvider, LLMProvider, MatchingEngine

__all__ = ['ASRProvider', 'TTSProvider', 'LLMProvider', 'MatchingEngine']
