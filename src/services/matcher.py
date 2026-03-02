"""
匹配引擎实现 - 基于特征的相似度匹配
"""
from typing import Dict, Any, List
import numpy as np

from ..core.base import MatchingEngine


class SimpleMatcher(MatchingEngine):
    """
    简化版匹配引擎
    
    使用余弦相似度进行特征向量匹配
    """
    
    @property
    def name(self) -> str:
        return "Simple Matcher"
    
    async def analyze_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析用户画像，提取特征
        
        Args:
            profile: 用户信息
                - age: 年龄
                - gender: 性别
                - interests: 兴趣列表
                - voice_features: 语音特征向量（可选）
                - personality: 性格特征（可选）
        
        Returns:
            特征字典
        """
        features = {}
        
        # 1. 基础特征
        features["age"] = profile.get("age", 25)
        features["gender"] = profile.get("gender", "unknown")
        
        # 2. 兴趣特征（转换为向量）
        interests = profile.get("interests", [])
        features["interest_vector"] = self._encode_interests(interests)
        
        # 3. 语音特征（气场）
        if "voice_features" in profile:
            features["voice_vector"] = np.array(profile["voice_features"])
        
        # 4. 性格特征
        if "personality" in profile:
            features["personality"] = profile["personality"]
        
        return features
    
    async def find_matches(
        self,
        user_features: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        找到最匹配的候选人
        
        Args:
            user_features: 当前用户特征
            candidates: 候选人列表
            top_k: 返回前K个
        
        Returns:
            匹配结果列表
        """
        scored_candidates = []
        
        for candidate in candidates:
            score = await self._calculate_similarity(user_features, candidate)
            
            scored_candidates.append({
                "user_id": candidate.get("user_id"),
                "score": float(score),
                "profile": candidate.get("profile", {}),
                "match_reasons": self._generate_match_reasons(user_features, candidate, score)
            })
        
        # 按分数排序
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_candidates[:top_k]
    
    async def _calculate_similarity(
        self,
        user_features: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> float:
        """
        计算相似度分数
        
        Returns:
            相似度分数（0-1）
        """
        scores = []
        
        # 1. 年龄相似度（越接近越好）
        user_age = user_features.get("age", 25)
        candidate_age = candidate.get("age", 25)
        age_score = 1.0 - abs(user_age - candidate_age) / 50.0
        scores.append(max(0, age_score) * 0.2)  # 权重20%
        
        # 2. 兴趣相似度
        user_interests = user_features.get("interest_vector", np.zeros(10))
        candidate_interests = candidate.get("interest_vector", np.zeros(10))
        
        if isinstance(user_interests, list):
            user_interests = np.array(user_interests)
        if isinstance(candidate_interests, list):
            candidate_interests = np.array(candidate_interests)
        
        interest_score = self._cosine_similarity(user_interests, candidate_interests)
        scores.append(interest_score * 0.4)  # 权重40%
        
        # 3. 语音特征相似度（如果有）
        if "voice_vector" in user_features and "voice_vector" in candidate:
            user_voice = user_features["voice_vector"]
            candidate_voice = candidate["voice_vector"]
            
            if isinstance(user_voice, list):
                user_voice = np.array(user_voice)
            if isinstance(candidate_voice, list):
                candidate_voice = np.array(candidate_voice)
            
            voice_score = self._cosine_similarity(user_voice, candidate_voice)
            scores.append(voice_score * 0.4)  # 权重40%
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _encode_interests(self, interests: List[str]) -> np.ndarray:
        """
        将兴趣列表编码为特征向量
        
        简化实现：使用预定义的兴趣类别
        """
        # 预定义兴趣类别（可根据实际需求扩展）
        interest_categories = [
            "音乐", "电影", "运动", "旅游", "美食",
            "阅读", "游戏", "摄影", "艺术", "科技"
        ]
        
        # 创建特征向量
        vector = np.zeros(len(interest_categories))
        
        for i, category in enumerate(interest_categories):
            if category in interests:
                vector[i] = 1.0
        
        return vector
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        if vec1.shape != vec2.shape:
            return 0.0
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def _generate_match_reasons(
        self,
        user_features: Dict[str, Any],
        candidate: Dict[str, Any],
        score: float
    ) -> List[str]:
        """
        生成匹配理由
        
        Returns:
            匹配理由列表
        """
        reasons = []
        
        # 年龄相近
        user_age = user_features.get("age", 25)
        candidate_age = candidate.get("age", 25)
        if abs(user_age - candidate_age) <= 3:
            reasons.append(f"年龄相仿（相差{abs(user_age - candidate_age)}岁）")
        
        # 共同兴趣
        user_interests = set(user_features.get("interests", []))
        candidate_interests = set(candidate.get("interests", []))
        common = user_interests & candidate_interests
        
        if common:
            reasons.append(f"共同兴趣：{', '.join(list(common)[:3])}")
        
        # 高匹配度
        if score > 0.8:
            reasons.append("语音气场高度契合")
        
        return reasons if reasons else ["综合评分较高"]
