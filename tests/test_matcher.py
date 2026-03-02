"""
测试匹配引擎
"""
import pytest
import numpy as np

from src.services.matcher import SimpleMatcher


class TestSimpleMatcher:
    """简化匹配引擎测试"""
    
    @pytest.fixture
    def matcher(self):
        """创建匹配引擎实例"""
        return SimpleMatcher()
    
    def test_name_property(self, matcher):
        """测试name属性"""
        assert matcher.name == "Simple Matcher"
    
    @pytest.mark.asyncio
    async def test_analyze_profile(self, matcher):
        """测试用户画像分析"""
        profile = {
            "age": 25,
            "gender": "male",
            "interests": ["音乐", "电影", "运动"],
            "personality": "开朗"
        }
        
        features = await matcher.analyze_profile(profile)
        
        # 验证特征提取
        assert features["age"] == 25
        assert features["gender"] == "male"
        assert "interest_vector" in features
        assert isinstance(features["interest_vector"], np.ndarray)
        assert len(features["interest_vector"]) == 10  # 10个兴趣类别
        assert features["personality"] == "开朗"
    
    @pytest.mark.asyncio
    async def test_analyze_profile_with_voice(self, matcher):
        """测试包含语音特征的画像分析"""
        profile = {
            "age": 28,
            "interests": ["旅游", "美食"],
            "voice_features": [0.1, 0.2, 0.3, 0.4]  # 简化的语音特征
        }
        
        features = await matcher.analyze_profile(profile)
        
        assert "voice_vector" in features
        assert len(features["voice_vector"]) == 4
    
    @pytest.mark.asyncio
    async def test_find_matches(self, matcher):
        """测试匹配功能"""
        # 用户特征
        user_features = {
            "age": 25,
            "interests": ["音乐", "电影", "运动"],
            "interest_vector": np.array([1, 1, 1, 0, 0, 0, 0, 0, 0, 0])
        }
        
        # 候选人列表
        candidates = [
            {
                "user_id": "user_001",
                "age": 26,
                "interests": ["音乐", "电影"],
                "interest_vector": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                "profile": {"name": "小明"}
            },
            {
                "user_id": "user_002",
                "age": 30,
                "interests": ["阅读", "游戏"],
                "interest_vector": [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                "profile": {"name": "小红"}
            },
            {
                "user_id": "user_003",
                "age": 25,
                "interests": ["音乐", "运动"],
                "interest_vector": [1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                "profile": {"name": "小李"}
            }
        ]
        
        matches = await matcher.find_matches(user_features, candidates, top_k=2)
        
        # 验证结果
        assert len(matches) == 2
        assert all("score" in m for m in matches)
        assert all("user_id" in m for m in matches)
        assert all("match_reasons" in m for m in matches)
        
        # 验证排序（分数降序）
        assert matches[0]["score"] >= matches[1]["score"]
    
    @pytest.mark.asyncio
    async def test_match_with_voice_similarity(self, matcher):
        """测试包含语音特征的匹配"""
        user_features = {
            "age": 25,
            "interests": ["音乐"],
            "interest_vector": np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            "voice_vector": np.array([0.5, 0.5, 0.5, 0.5])
        }
        
        candidates = [
            {
                "user_id": "user_001",
                "age": 25,
                "interest_vector": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "voice_vector": [0.5, 0.5, 0.5, 0.5],  # 完全相同
                "profile": {}
            },
            {
                "user_id": "user_002",
                "age": 25,
                "interest_vector": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "voice_vector": [0.1, 0.1, 0.1, 0.1],  # 完全不同
                "profile": {}
            }
        ]
        
        matches = await matcher.find_matches(user_features, candidates)
        
        # 语音特征相同的应该得分更高
        assert matches[0]["user_id"] == "user_001"
    
    def test_encode_interests(self, matcher):
        """测试兴趣编码"""
        interests = ["音乐", "电影", "科技"]
        
        vector = matcher._encode_interests(interests)
        
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 10
        # 验证对应位置被激活
        assert vector[0] == 1  # 音乐
        assert vector[1] == 1  # 电影
        assert vector[9] == 1  # 科技
    
    def test_cosine_similarity(self, matcher):
        """测试余弦相似度计算"""
        vec1 = np.array([1, 0, 1])
        vec2 = np.array([1, 1, 0])
        
        similarity = matcher._cosine_similarity(vec1, vec2)
        
        # 手动计算：(1*1 + 0*1 + 1*0) / (sqrt(2) * sqrt(2)) = 1/2 = 0.5
        assert 0.49 < similarity < 0.51
    
    def test_cosine_similarity_zero_vectors(self, matcher):
        """测试零向量情况"""
        vec1 = np.array([0, 0, 0])
        vec2 = np.array([1, 1, 1])
        
        similarity = matcher._cosine_similarity(vec1, vec2)
        
        assert similarity == 0.0
    
    @pytest.mark.asyncio
    async def test_match_reasons_generation(self, matcher):
        """测试匹配理由生成"""
        user_features = {
            "age": 25,
            "interests": ["音乐", "电影"]
        }
        
        candidate = {
            "age": 26,
            "interests": ["音乐", "运动"]
        }
        
        reasons = matcher._generate_match_reasons(user_features, candidate, 0.9)
        
        # 验证生成的理由
        assert isinstance(reasons, list)
        assert len(reasons) > 0
        assert any("年龄" in r or "兴趣" in r for r in reasons)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
