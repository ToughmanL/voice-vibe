"""
集成测试 - 测试整体流程
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.config_loader import ConfigLoader


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def config(self):
        """加载配置"""
        return ConfigLoader()
    
    def test_config_loading(self, config):
        """测试配置加载"""
        # 验证讯飞配置
        assert config.xunfei_asr['appid'] is not None
        assert config.xunfei_asr['api_key'] is not None
        assert config.xunfei_asr['api_secret'] is not None
        
        # 验证Kimi配置
        assert config.kimi['api_key'] is not None
        assert config.kimi['base_url'] is not None
    
    def test_auth_url_generation(self, config):
        """测试鉴权URL生成"""
        asr_url = config.get_xunfei_auth_url("asr")
        tts_url = config.get_xunfei_auth_url("tts")
        
        assert asr_url.startswith("wss://")
        assert "iat" in asr_url
        assert tts_url.startswith("wss://")
        assert "tts" in tts_url
    
    @pytest.mark.asyncio
    async def test_end_to_end_flow_mock(self, config):
        """测试端到端流程（模拟所有服务）"""
        from src.providers import XunfeiASRClient, XunfeiTTSClient, KimiLLMClient
        from src.services import SimpleMatcher
        
        # 初始化所有服务
        asr = XunfeiASRClient(
            appid=config.xunfei_asr['appid'],
            api_key=config.xunfei_asr['api_key'],
            api_secret=config.xunfei_asr['api_secret']
        )
        
        tts = XunfeiTTSClient(
            appid=config.xunfei_tts['appid'],
            api_key=config.xunfei_tts['api_key'],
            api_secret=config.xunfei_tts['api_secret']
        )
        
        llm = KimiLLMClient(
            api_key=config.kimi['api_key'],
            base_url=config.kimi['base_url'],
            model=config.kimi['model']
        )
        
        matcher = SimpleMatcher()
        
        # 验证所有服务都初始化成功
        assert asr.name == "Xunfei ASR"
        assert tts.name == "Xunfei TTS"
        assert llm.name == "Kimi LLM"
        assert matcher.name == "Simple Matcher"
        
        # 模拟完整流程
        # 1. 用户画像分析
        user_profile = {
            "age": 25,
            "interests": ["音乐", "电影"]
        }
        
        features = await matcher.analyze_profile(user_profile)
        assert features is not None
        
        # 2. 匹配
        matches = await matcher.find_matches(features, [], top_k=3)
        assert isinstance(matches, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
