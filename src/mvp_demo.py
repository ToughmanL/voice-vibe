#!/usr/bin/env python3
"""
AI语音匹配产品 - MVP Demo
快速体验核心功能：语音对话 → 气场分析 → 匹配推荐

运行方式:
1. 安装依赖: pip install fastapi uvicorn websockets openai numpy scipy
2. 配置API: export OPENAI_API_KEY=your-key
3. 运行: python mvp_demo.py
4. 访问: http://localhost:8000
"""

import asyncio
import json
import numpy as np
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ============== 数据模型 ==============

@dataclass
class AuraProfile:
    """气场画像"""
    user_id: str
    aura_vector: List[float] = field(default_factory=lambda: [0.0] * 16)  # 简化为16维
    traits: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "traits": self.traits,
            "aura_vector": self.aura_vector[:4],  # 只显示前4维
            "created_at": self.created_at.isoformat()
        }

@dataclass  
class User:
    """用户"""
    user_id: str
    name: str
    profile: AuraProfile
    conversation_history: List[Dict] = field(default_factory=list)

@dataclass
class MatchResult:
    """匹配结果"""
    user: User
    score: float
    explanation: str

# ============== 模拟数据库 ==============

class MockDatabase:
    """模拟数据库 - MVP阶段"""
    
    def __init__(self):
        # 预置一些模拟用户
        self.users = self._create_mock_users()
    
    def _create_mock_users(self) -> Dict[str, User]:
        """创建模拟用户数据"""
        mock_data = [
            {
                "user_id": "u001",
                "name": "小雨",
                "traits": {"温柔": 0.8, "理性": 0.6, "幽默": 0.7, "独立": 0.5},
                "aura_vector": [0.6, 0.4, 0.7, 0.3, 0.5, 0.8, 0.4, 0.6, 0.7, 0.5, 0.3, 0.8, 0.6, 0.4, 0.7, 0.5]
            },
            {
                "user_id": "u002", 
                "name": "明轩",
                "traits": {"自信": 0.9, "温和": 0.7, "有趣": 0.8, "稳重": 0.6},
                "aura_vector": [0.8, 0.6, 0.5, 0.7, 0.8, 0.4, 0.7, 0.5, 0.6, 0.8, 0.7, 0.4, 0.5, 0.8, 0.6, 0.7]
            },
            {
                "user_id": "u003",
                "name": "思琪",
                "traits": {"活泼": 0.9, "善良": 0.8, "聪明": 0.7, "体贴": 0.8},
                "aura_vector": [0.7, 0.8, 0.6, 0.5, 0.9, 0.6, 0.5, 0.8, 0.4, 0.7, 0.8, 0.6, 0.5, 0.7, 0.8, 0.6]
            },
            {
                "user_id": "u004",
                "name": "浩然",
                "traits": {"成熟": 0.8, "幽默": 0.7, "上进": 0.9, "真诚": 0.8},
                "aura_vector": [0.5, 0.6, 0.8, 0.7, 0.6, 0.7, 0.8, 0.5, 0.7, 0.6, 0.5, 0.7, 0.8, 0.6, 0.5, 0.8]
            }
        ]
        
        users = {}
        for data in mock_data:
            profile = AuraProfile(
                user_id=data["user_id"],
                traits=data["traits"],
                aura_vector=data["aura_vector"]
            )
            users[data["user_id"]] = User(
                user_id=data["user_id"],
                name=data["name"],
                profile=profile
            )
        
        return users
    
    def get_all_users(self) -> List[User]:
        return list(self.users.values())

# ============== 气场分析引擎 ==============

class AuraAnalyzer:
    """气场分析器 - MVP简化版"""
    
    # 特征维度映射
    DIMENSION_MEANINGS = {
        0: "能量水平",
        1: "表达活跃度", 
        2: "情绪丰富度",
        3: "理性程度",
        4: "外向程度",
        5: "温柔程度",
        6: "自信程度",
        7: "幽默程度"
    }
    
    async def analyze_from_text(self, text: str, audio_features: Optional[Dict] = None) -> AuraProfile:
        """从文本分析气场（MVP阶段简化）"""
        
        # 简化版：基于文本特征推断
        features = self._extract_text_features(text)
        
        # 生成16维气场向量
        aura_vector = self._generate_aura_vector(features, audio_features)
        
        # 解释为可读标签
        traits = self._interpret_traits(aura_vector)
        
        return AuraProfile(
            user_id="current",
            aura_vector=aura_vector,
            traits=traits
        )
    
    def _extract_text_features(self, text: str) -> Dict[str, float]:
        """从文本提取特征"""
        features = {}
        
        # 基于关键词的简单规则（实际应使用LLM）
        text_lower = text.lower()
        
        # 情绪词
        positive_words = ["开心", "高兴", "喜欢", "热爱", "期待", "美好"]
        negative_words = ["担心", "焦虑", "压力", "困惑", "迷茫"]
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        features["sentiment"] = (pos_count - neg_count) / max(pos_count + neg_count + 1, 1)
        
        # 表达长度 - 反映开放程度
        features["expression_level"] = min(len(text) / 100, 1.0)
        
        # 问号数量 - 反映好奇心
        features["curiosity"] = min(text.count("?") + text.count("？"), 1.0)
        
        # 感叹号 - 反映情绪强度
        features["emotion_intensity"] = min(text.count("!") + text.count("！") * 0.2, 1.0)
        
        return features
    
    def _generate_aura_vector(self, features: Dict, audio_features: Optional[Dict] = None) -> List[float]:
        """生成气场向量"""
        # 基础向量（基于文本）
        base_vector = [
            0.5 + features.get("sentiment", 0) * 0.3,      # 能量水平
            features.get("expression_level", 0.5),          # 表达活跃度
            0.5 + features.get("emotion_intensity", 0) * 0.3,  # 情绪丰富度
            0.6 - features.get("emotion_intensity", 0) * 0.2,  # 理性程度
            features.get("curiosity", 0.5),                  # 外向/好奇
            0.6,  # 温柔程度（默认中等）
            0.5 + features.get("sentiment", 0) * 0.2,       # 自信程度
            0.5,  # 幽默程度
        ]
        
        # 添加8维随机噪声（模拟复杂度）
        noise = np.random.normal(0, 0.1, 8).tolist()
        
        # 合并为16维
        aura_vector = base_vector + noise
        
        # 归一化到0-1
        aura_vector = [max(0, min(1, v)) for v in aura_vector]
        
        return aura_vector
    
    def _interpret_traits(self, aura_vector: List[float]) -> Dict[str, float]:
        """解释气场向量为可读特征"""
        traits = {}
        
        # 基于向量值判断特征
        if aura_vector[0] > 0.6:
            traits["积极乐观"] = aura_vector[0]
        elif aura_vector[0] < 0.4:
            traits["内敛沉稳"] = 1 - aura_vector[0]
            
        if aura_vector[1] > 0.6:
            traits["表达力强"] = aura_vector[1]
        
        if aura_vector[2] > 0.6:
            traits["情感丰富"] = aura_vector[2]
        elif aura_vector[3] > 0.6:
            traits["理性思考"] = aura_vector[3]
            
        if aura_vector[4] > 0.5:
            traits["好奇心强"] = aura_vector[4]
        
        if aura_vector[5] > 0.5:
            traits["温柔体贴"] = aura_vector[5]
            
        if aura_vector[6] > 0.6:
            traits["自信独立"] = aura_vector[6]
        
        # 确保至少有3个特征
        if len(traits) < 3:
            traits["真诚可靠"] = 0.7
            
        return traits

# ============== 匹配引擎 ==============

class MatchEngine:
    """匹配引擎"""
    
    def __init__(self, db: MockDatabase, analyzer: AuraAnalyzer):
        self.db = db
        self.analyzer = analyzer
    
    async def find_matches(
        self, 
        user_profile: AuraProfile, 
        top_k: int = 3
    ) -> List[MatchResult]:
        """找匹配"""
        
        candidates = self.db.get_all_users()
        matches = []
        
        for candidate in candidates:
            # 计算气场相似度
            score = self._calculate_similarity(
                user_profile.aura_vector,
                candidate.profile.aura_vector
            )
            
            # 生成匹配解释
            explanation = self._generate_explanation(
                user_profile, 
                candidate.profile, 
                score
            )
            
            matches.append(MatchResult(
                user=candidate,
                score=score,
                explanation=explanation
            ))
        
        # 排序取top_k
        matches.sort(key=lambda x: x.score, reverse=True)
        return matches[:top_k]
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # 余弦相似度
        similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        
        # 转换为0-100分
        score = (similarity + 1) / 2 * 100
        
        # 添加随机因素（模拟复杂匹配逻辑）
        score += np.random.uniform(-5, 5)
        
        return round(max(0, min(100, score)), 1)
    
    def _generate_explanation(
        self, 
        profile1: AuraProfile, 
        profile2: AuraProfile,
        score: float
    ) -> str:
        """生成匹配解释"""
        
        # 找共同特质
        common_traits = set(profile1.traits.keys()) & set(profile2.traits.keys())
        
        if common_traits:
            traits_str = "、".join(list(common_traits)[:2])
            return f"你们都很{traits_str}，气场很合！"
        else:
            # 找互补特质
            return f"你们的性格互补，可能会擦出不一样的火花～"

# ============== 对话管理 ==============

class ConversationManager:
    """对话管理器"""
    
    def __init__(self):
        self.questions = [
            "嗨！我是AI匹配助手。首先，能跟我说说最近让你开心的一件事吗？",
            "听起来不错！那你平时喜欢做什么来放松自己呢？",
            "很有意思！在感情里，你最看重对方什么品质？",
            "最后一个问题，你理想中的周末是怎么过的？"
        ]
        self.current_step = 0
        self.responses = []
    
    def get_next_question(self) -> Optional[str]:
        """获取下一个问题"""
        if self.current_step < len(self.questions):
            return self.questions[self.current_step]
        return None
    
    def add_response(self, response: str):
        """添加用户回复"""
        self.responses.append(response)
        self.current_step += 1
    
    def is_complete(self) -> bool:
        """是否完成对话"""
        return self.current_step >= len(self.questions)
    
    def get_all_responses(self) -> str:
        """获取所有回复"""
        return " ".join(self.responses)

# ============== 主应用 ==============

app = FastAPI(title="AI语音匹配 Demo")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
db = MockDatabase()
aura_analyzer = AuraAnalyzer()
match_engine = MatchEngine(db, aura_analyzer)

@app.get("/")
async def index():
    """主页"""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI语音匹配 Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .chat-area {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #eee;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            background: #f9f9f9;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
        }
        .ai {
            background: #667eea;
            color: white;
            margin-right: auto;
        }
        .user {
            background: #e0e0e0;
            color: #333;
            margin-left: auto;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #eee;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        input:focus {
            border-color: #667eea;
        }
        button {
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            background: #5a6fd6;
            transform: translateY(-2px);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .matches {
            margin-top: 20px;
        }
        .match-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .match-name {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .match-score {
            color: #667eea;
            font-size: 24px;
            font-weight: bold;
        }
        .match-explanation {
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }
        .traits {
            margin-top: 10px;
        }
        .trait-tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        .status {
            text-align: center;
            color: #666;
            padding: 10px;
            font-size: 14px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .loading.active {
            display: block;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI语音匹配 Demo</h1>
        <p class="subtitle">通过对话了解你，为你找到气场相合的人</p>
        
        <div class="chat-area" id="chatArea">
            <div class="status">点击下方按钮开始</div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>AI正在分析你的气场...</div>
        </div>
        
        <div class="input-area">
            <input type="text" id="userInput" placeholder="输入你的回答..." disabled>
            <button id="sendBtn" onclick="sendMessage()">发送</button>
        </div>
        
        <div class="matches" id="matches"></div>
    </div>

    <script>
        let ws;
        let isStarted = false;
        
        function connect() {
            ws = new WebSocket('ws://' + location.host + '/ws');
            
            ws.onopen = function() {
                console.log('Connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function() {
                console.log('Disconnected');
            };
        }
        
        function handleMessage(data) {
            const chatArea = document.getElementById('chatArea');
            const input = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            const loading = document.getElementById('loading');
            
            if (data.type === 'question') {
                loading.classList.remove('active');
                addMessage(data.content, 'ai');
                input.disabled = false;
                sendBtn.disabled = false;
                input.focus();
            } 
            else if (data.type === 'complete') {
                loading.classList.add('active');
                addMessage(data.content, 'ai');
                input.disabled = true;
                sendBtn.disabled = true;
            }
            else if (data.type === 'matches') {
                loading.classList.remove('active');
                displayMatches(data.matches);
            }
            else if (data.type === 'profile') {
                displayProfile(data.profile);
            }
        }
        
        function addMessage(text, type) {
            const chatArea = document.getElementById('chatArea');
            const msg = document.createElement('div');
            msg.className = 'message ' + type;
            msg.textContent = text;
            chatArea.appendChild(msg);
            chatArea.scrollTop = chatArea.scrollHeight;
        }
        
        function sendMessage() {
            const input = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            const text = input.value.trim();
            
            if (!text) return;
            
            addMessage(text, 'user');
            
            ws.send(JSON.stringify({
                type: 'response',
                content: text
            }));
            
            input.value = '';
            input.disabled = true;
            sendBtn.disabled = true;
        }
        
        function displayProfile(profile) {
            // 显示用户画像
            console.log('Profile:', profile);
        }
        
        function displayMatches(matches) {
            const container = document.getElementById('matches');
            container.innerHTML = '<h3 style="margin-bottom:15px;color:#333;">为你推荐：</h3>';
            
            matches.forEach((match, index) => {
                const card = document.createElement('div');
                card.className = 'match-card';
                
                let traitsHtml = '';
                for (const [trait, value] of Object.entries(match.user.profile.traits)) {
                    traitsHtml += `<span class="trait-tag">${trait}</span>`;
                }
                
                card.innerHTML = `
                    <div class="match-name">${match.user.name}</div>
                    <div class="match-score">匹配度: ${match.score}%</div>
                    <div class="match-explanation">${match.explanation}</div>
                    <div class="traits">${traitsHtml}</div>
                `;
                
                container.appendChild(card);
            });
        }
        
        function startChat() {
            if (!isStarted) {
                connect();
                isStarted = true;
                
                // 发送开始信号
                setTimeout(() => {
                    ws.send(JSON.stringify({type: 'start'}));
                }, 100);
            }
        }
        
        // 回车发送
        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // 页面加载后自动开始
        window.onload = function() {
            setTimeout(startChat, 500);
        };
    </script>
</body>
</html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket对话入口"""
    await websocket.accept()
    
    conv_manager = ConversationManager()
    user_responses = []
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "start":
                # 开始对话
                first_question = conv_manager.get_next_question()
                if first_question:
                    await websocket.send_json({
                        "type": "question",
                        "content": first_question
                    })
            
            elif message["type"] == "response":
                # 用户回复
                user_response = message["content"]
                user_responses.append(user_response)
                conv_manager.add_response(user_response)
                
                # 检查是否完成
                if conv_manager.is_complete():
                    # 完成对话，开始分析
                    await websocket.send_json({
                        "type": "complete",
                        "content": "太好了！让我来分析一下你的气场特征..."
                    })
                    
                    # 分析气场
                    all_text = " ".join(user_responses)
                    user_profile = await aura_analyzer.analyze_from_text(all_text)
                    
                    # 发送画像
                    await websocket.send_json({
                        "type": "profile",
                        "profile": user_profile.to_dict()
                    })
                    
                    # 匹配
                    matches = await match_engine.find_matches(user_profile)
                    
                    # 发送匹配结果
                    await websocket.send_json({
                        "type": "matches",
                        "matches": [
                            {
                                "user": {
                                    "name": m.user.name,
                                    "profile": m.user.profile.to_dict()
                                },
                                "score": m.score,
                                "explanation": m.explanation
                            }
                            for m in matches
                        ]
                    })
                else:
                    # 继续下一个问题
                    next_question = conv_manager.get_next_question()
                    if next_question:
                        await websocket.send_json({
                            "type": "question",
                            "content": next_question
                        })
    
    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/api/users")
async def get_users():
    """获取所有用户"""
    return [u.user_id for u in db.get_all_users()]

@app.post("/api/analyze")
async def analyze_text(text: str):
    """分析文本气场"""
    profile = await aura_analyzer.analyze_from_text(text)
    return profile.to_dict()

@app.post("/api/match")
async def match_users(text: str):
    """根据文本匹配"""
    profile = await aura_analyzer.analyze_from_text(text)
    matches = await match_engine.find_matches(profile)
    return {
        "profile": profile.to_dict(),
        "matches": [
            {
                "user": m.user.name,
                "score": m.score,
                "explanation": m.explanation
            }
            for m in matches
        ]
    }

if __name__ == "__main__":
    print("=" * 50)
    print("AI语音匹配 Demo")
    print("=" * 50)
    print(f"访问地址: http://localhost:8000")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
