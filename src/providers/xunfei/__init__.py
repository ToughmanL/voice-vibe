"""
讯飞服务提供者
"""
from .asr_client import XunfeiASRClient
from .tts_client import XunfeiTTSClient

__all__ = ['XunfeiASRClient', 'XunfeiTTSClient']
