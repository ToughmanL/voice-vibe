# AI语音匹配产品技术架构方案

> 基于语音交互+情感计算+多Agent协作的婚恋匹配平台

---

## 1. 总体技术愿景与设计哲学

### 1.1 "懒人式脱单"的实现路径

用户只需开口说话，AI全程托管：
- **零填表**：通过自然语音对话自动提取用户画像（价值观、兴趣、择偶偏好）
- **被动匹配**：AI主动分析、主动推荐、主动安排，用户只需做最终确认
- **效果付费**：用户为结果买单（见面、订餐），而非为过程付费

```
用户说：我最近工作压力大，想找个能聊得来的人
AI做：[语音情感分析] → [意图解析] → [画像更新] → [候选匹配] → [主动推送]
```

### 1.2 三层解耦架构

| 层级 | 职责 | 核心技术 | 解耦收益 |
|------|------|----------|----------|
| **交互层** | 语音I/O、实时性 | WebSocket + VAD + ASR/TTS | 可替换语音服务商 |
| **认知层** | 业务逻辑、决策 | 多Agent协作系统 | 可扩展Agent类型 |
| **数据层** | 状态持久化、检索 | 向量库 + 关系库 | 可独立扩容 |

**设计原则**：
- 每层可独立部署、独立扩容
- 层间通过消息队列解耦
- 状态无服务化，便于水平扩展

---

## 2. 全链路技术架构

### 2.1 架构图（文字描述）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户端 (macOS App)                              │
│                    WebSocket + WebRTC (实时语音流)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              交互层 (语音网关)                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│  │  VAD     │→ │  ASR     │→ │ 断句引擎 │→ │  TTS     │                    │
│  │ 静音检测 │  │ 语音转文 │  │ 语义边界 │  │ 文转语音 │                    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                    │
│        │              │              │              ↑                       │
│        └──────────────┴──────────────┴──────────────┘                       │
│                         音频缓冲区 (环形队列)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                        消息队列 (Redis Stream / Kafka)
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           认知层 (多Agent协作)                               │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     主持Agent (Orchestrator)                        │   │
│   │   - 任务调度中心                                                    │   │
│   │   - 对话状态机管理                                                  │   │
│   │   - Agent间协调                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                    │              │              │                           │
│        ┌───────────┴───────┐ ┌────┴────┐ ┌──────┴─────────┐                 │
│        │   情感计算Agent   │ │意图Agent│ │   匹配Agent    │                 │
│        │                   │ │         │ │                │                 │
│        │ • 语速/音量/音高  │ │• 价值观 │ │ • 向量相似度  │                 │
│        │ • 颤音/停顿模式   │ │• 兴趣点 │ │ • 规则过滤    │                 │
│        │ • 笑声/填充词    │ │• 择偶标准│ │ • 匹配解释    │                 │
│        │ • 气场特征向量   │ │• 情感需求│ │ • 排序策略    │                 │
│        └───────────────────┘ └─────────┘ └────────────────┘                 │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     LLM编排层 (LangChain)                           │   │
│   │   Prompt模板 | 记忆管理 | 工具调用 | 输出解析                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据层                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  向量数据库   │  │  用户画像库  │  │  标注样本库  │  │  会话状态库  │   │
│  │  (Milvus)    │  │  (PostgreSQL)│  │  (PostgreSQL)│  │  (Redis)     │   │
│  │              │  │              │  │              │  │              │   │
│  │ • 气场向量   │  │ • 基础信息   │  │ • 标注数据   │  │ • 对话历史   │   │
│  │ • 语义向量   │  │ • 情感画像   │  │ • 专家标签   │  │ • 用户状态   │   │
│  │ • 混合索引   │  │ • 匹配历史   │  │ • 反馈记录   │  │ • 缓存数据   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型（MVP阶段）

| 组件 | 选型 | 原因 |
|------|------|------|
| ASR | 阿里云语音识别 / 讯飞 | 中文识别准确，流式API成熟 |
| TTS | Azure Speech / 阿里云 | 情感丰富，延迟低（<200ms） |
| LLM | GPT-4o / 通义千问 | 多模态理解，长上下文 |
| Agent框架 | LangChain | 生态成熟，工具丰富 |
| 向量库 | Milvus / Zilliz Cloud | 高性能，支持混合检索 |
| 消息队列 | Redis Stream | MVP阶段足够，运维简单 |
| 主数据库 | PostgreSQL | 可靠，支持JSONB |

---

## 3. 核心难题攻坚方案

### 3.1 AI语音实时交互延迟

**目标端到端延迟**：< 800ms（从用户说完到AI开始回复）

#### 3.1.1 流式处理Pipeline

```
用户语音 ──┬──→ [VAD检测] ──→ [分段] ──→ [ASR流式] ──→ [中间文本]
           │        │            │            │
           │     检测静音     按500ms      实时返回
           │     300ms窗口    切分         增量结果
           │
           └──→ [音频缓冲] ──→ [情感特征提取] ──→ [气场向量]
                                           │
                                     异步处理，不阻塞主流程
```

#### 3.1.2 关键优化策略

| 策略 | 实现方式 | 效果 |
|------|----------|------|
| **全双工通信** | WebSocket长连接，上行语音与下行回复并行 | 节省连接建立时间 |
| **VAD提前触发** | 静音300ms即判定段落结束，无需等用户明确说"完了" | 减少200-500ms等待 |
| **ASR流式识别** | 边说边识别，中间结果实时回调 | 提前500-1000ms获得文本 |
| **LLM流式输出** | 收到首个token即开始TTS合成 | 首字延迟降低至100-200ms |
| **TTS预合成** | 常用开场白/过渡语预缓存 | 热门回复0延迟 |
| **并发处理** | ASR结果 → 同时触发意图+情感分析 | 并行处理节省时间 |

#### 3.1.3 "类人"对话节奏

```python
# 对话节奏控制伪代码
class ConversationRhythm:
    def should_respond(self, silence_duration, context):
        # 1. 短停顿（300-500ms）- 可能只是换气
        if silence_duration < 0.5 and not self.is_question_context(context):
            return False  # 继续等待
        
        # 2. 中等停顿（500-800ms）- 用户思考中
        if 0.5 <= silence_duration < 0.8:
            # 用"嗯..."等填充词表示倾听
            return self.emit_filler_sound("嗯")
        
        # 3. 长停顿（>800ms）- 用户说完了
        if silence_duration >= 0.8:
            return self.start_response()
        
        # 4. 智能打断 - 检测到完整语义单元
        if self.is_complete_thought(context):
            return self.start_response()
```

### 3.2 多Agent协作系统

#### 3.2.1 基于LangChain的Agent框架

```python
from langchain.agents import AgentExecutor
from langchain.schema import AgentAction
from typing import TypedDict, List

# Agent通信协议
class AgentMessage(TypedDict):
    sender: str          # 发送Agent ID
    receiver: str        # 接收Agent ID (或 "broadcast")
    message_type: str    # request / response / event
    payload: dict        # 实际数据
    timestamp: float
    correlation_id: str  # 请求关联ID

# 主持Agent - 任务调度核心
class OrchestratorAgent:
    """
    职责：
    1. 接收用户输入，决定调用哪些Agent
    2. 协调Agent执行顺序
    3. 合并多Agent结果
    4. 管理对话状态机
    """
    
    def __init__(self):
        self.state_machine = ConversationStateMachine()
        self.agents = {
            "emotion": EmotionAgent(),
            "intent": IntentAgent(), 
            "match": MatchAgent()
        }
    
    async def process_user_input(self, audio_segment, transcript):
        # 1. 并行调用情感和意图Agent
        emotion_task = self.agents["emotion"].analyze(audio_segment)
        intent_task = self.agents["intent"].analyze(transcript)
        
        emotion_result, intent_result = await asyncio.gather(
            emotion_task, intent_task
        )
        
        # 2. 根据意图决定是否触发匹配
        if intent_result.get("needs_matching"):
            match_result = await self.agents["match"].find_candidates(
                emotion_vector=emotion_result["aura_vector"],
                intent_profile=intent_result["profile_update"]
            )
        else:
            match_result = None
        
        # 3. 生成回复
        response = await self.generate_response(
            emotion=emotion_result,
            intent=intent_result,
            match=match_result
        )
        
        return response

# 情感计算Agent
class EmotionAgent:
    """提取气场特征向量"""
    
    async def analyze(self, audio_segment) -> dict:
        # 1. 声学特征提取
        acoustic_features = self.extract_acoustic_features(audio_segment)
        # 包含：语速、音量均值/方差、基频F0、共振峰、颤音频率
        
        # 2. 韵律特征
        prosody_features = self.extract_prosody(audio_segment)
        # 包含：停顿分布、重音模式、语调曲线
        
        # 3. 填充词检测
        filler_words = self.detect_fillers(audio_segment)
        # 包含："嗯""啊""那个"的频率和分布
        
        # 4. 融合成气场向量
        aura_vector = self.encode_aura(
            acoustic_features,
            prosody_features, 
            filler_words
        )
        
        return {
            "aura_vector": aura_vector,  # 128维向量
            "features": {
                "speech_rate": acoustic_features["speech_rate"],
                "energy_pattern": acoustic_features["energy"],
                "pitch_variation": acoustic_features["f0_std"],
                "filler_count": filler_words["total_count"],
                "confidence_level": self.infer_confidence(acoustic_features)
            }
        }

# 意图识别Agent
class IntentAgent:
    """解析用户语义，提取结构化信息"""
    
    INTENT_PROMPT = """
    分析用户对话，提取以下信息（JSON格式）：
    
    1. current_intent: 当前意图
       - share_feeling: 分享心情
       - seek_advice: 寻求建议  
       - update_preference: 更新择偶偏好
       - check_matches: 查看匹配
       - arrange_date: 安排约会
       - casual_chat: 闲聊
    
    2. profile_updates: 画像更新字段
       - values: 价值观关键词
       - interests: 兴趣标签
       - requirements: 择偶要求
    
    3. emotional_state: 当前情绪
       - valence: 积极/消极 (-1到1)
       - arousal: 平静/激动 (0到1)
    
    4. needs_matching: 是否需要触发匹配 (bool)
    
    用户输入: {transcript}
    对话历史: {history}
    """
    
    async def analyze(self, transcript) -> dict:
        response = await self.llm.ainvoke(
            self.INTENT_PROMPT.format(
                transcript=transcript,
                history=self.get_recent_history()
            )
        )
        return self.parse_response(response)

# 匹配Agent
class MatchAgent:
    """基于气场+语义的匹配计算"""
    
    async def find_candidates(
        self, 
        emotion_vector: List[float],
        intent_profile: dict
    ) -> dict:
        
        # 1. 向量相似度搜索（气场匹配）
        aura_candidates = await self.vector_db.search(
            collection="user_aura",
            query_vector=emotion_vector,
            top_k=50,
            filter={"gender": intent_profile.get("preferred_gender")}
        )
        
        # 2. 语义相似度（价值观/兴趣匹配）
        semantic_candidates = await self.vector_db.search(
            collection="user_semantic",
            query_text=intent_profile.get("values_interests_text"),
            top_k=50
        )
        
        # 3. 混合排序
        merged = self.merge_and_rank(
            aura_candidates,      # 权重 0.6
            semantic_candidates,  # 权重 0.3
            activity_score=0.1    # 活跃度
        )
        
        # 4. 规则过滤
        filtered = self.apply_hard_filters(merged, intent_profile)
        
        # 5. 生成匹配解释
        top_matches = filtered[:5]
        explanations = await self.generate_match_explanations(top_matches)
        
        return {
            "candidates": top_matches,
            "explanations": explanations,
            "total_count": len(filtered)
        }
```

#### 3.2.2 解决Agent幻觉与任务冲突

| 问题 | 解决方案 |
|------|----------|
| **幻觉** | 1. 结构化输出（强制JSON schema）<br>2. 事实核查（匹配结果必须来自数据库真实记录）<br>3. 置信度阈值（低置信度时转人工） |
| **任务冲突** | 1. 主持Agent作为唯一决策者<br>2. Agent只返回结果，不直接响应用户<br>3. 状态机管理对话阶段，明确每个阶段可执行的Agent |
| **输出不一致** | 1. 共享记忆（所有Agent读写同一对话状态）<br>2. 结果校验（主持Agent合并前检查逻辑一致性） |

```python
# 状态机控制对话流程
class ConversationStateMachine:
    STATES = {
        "onboarding": "新用户引导",
        "profiling": "画像收集",
        "matching": "匹配推荐", 
        "dating": "约会安排",
        "feedback": "反馈收集"
    }
    
    TRANSITIONS = {
        "onboarding": ["profiling"],
        "profiling": ["matching", "profiling"],  # 可循环补充信息
        "matching": ["dating", "profiling"],      # 不满意则返回补充
        "dating": ["feedback", "matching"],
        "feedback": ["matching", "end"]
    }
    
    def can_execute_agent(self, current_state: str, agent_name: str) -> bool:
        """根据当前状态判断Agent是否可执行"""
        AGENT_STATE_MAP = {
            "EmotionAgent": ["profiling", "matching", "feedback"],
            "IntentAgent": "all",  # 所有状态都可执行
            "MatchAgent": ["matching"],
        }
        allowed_states = AGENT_STATE_MAP.get(agent_name, [])
        return allowed_states == "all" or current_state in allowed_states
```

### 3.3 情感特征提取（气场匹配核心技术）

#### 3.3.1 技术路径

**推荐方案：开源工具 + 轻量化模型**

```
原始音频 → [预处理] → [opensmile提取] → [特征工程] → [轻量编码器] → 气场向量
           降噪/归一化   6513维eGeMAPS    降维/统计     ONNX小模型    128维
```

**原因**：
1. 直接调用语音情感API（如Azure情感识别）只返回"开心/悲伤"等粗粒度标签，无法做精细匹配
2. opensmile是领域标准工具，可提取全面的声学特征
3. 轻量编码器可在CPU上实时运行

#### 3.3.2 具体实现

```python
import opensmile
import numpy as np
from sklearn.preprocessing import StandardScaler
import onnxruntime as ort

class AuraFeatureExtractor:
    """
    气场特征提取器
    
    气场维度定义：
    1. 能量场：音量、能量分布
    2. 节奏场：语速、停顿模式
    3. 情绪场：音高变化、颤音
    4. 表达场：填充词、笑声频率
    """
    
    def __init__(self):
        # opensmile配置 - 使用eGeMAPS标准特征集
        self.smile = opensmile.Smile(
            feature_set=opensmile.FeatureSet.eGeMAPSv02,
            feature_level=opensmile.FeatureLevel.Functionals,
        )
        
        # 轻量编码器（ONNX格式，~5MB）
        self.encoder = ort.InferenceSession("models/aura_encoder.onnx")
        self.scaler = StandardScaler()
        
    def extract(self, audio_path: str) -> np.ndarray:
        # 1. opensmile提取6513维特征
        features_df = self.smile.process_file(audio_path)
        features = features_df.values.flatten()  # (6513,)
        
        # 2. 特征分组
        acoustic_features = self.group_features(features)
        
        # 3. 特征工程 - 提取关键维度
        engineered = self.feature_engineering(acoustic_features)
        
        # 4. 编码为气场向量
        aura_vector = self.encode(engineered)
        
        return aura_vector  # (128,)
    
    def group_features(self, features):
        """将6513维特征分组"""
        return {
            # 能量相关（音量、能量）
            "energy": features[0:200],
            
            # 频谱相关（音色、音质）
            "spectral": features[200:1500],
            
            # 基频相关（音高、语调）
            "f0": features[1500:2500],
            
            # 韵律相关（节奏、停顿）
            "prosody": features[2500:4000],
            
            # 音质相关（颤音、气息）
            "voice_quality": features[4000:5000],
            
            # 其他
            "other": features[5000:]
        }
    
    def feature_engineering(self, grouped_features):
        """特征工程 - 提取有意义的高层特征"""
        engineered = []
        
        # 1. 能量场
        energy = grouped_features["energy"]
        engineered.extend([
            np.mean(energy),      # 平均能量（整体音量）
            np.std(energy),       # 能量变化（抑扬顿挫）
            np.max(energy),       # 最大能量（爆发力）
            np.mean(np.diff(energy)),  # 能量趋势
        ])
        
        # 2. 节奏场
        f0 = grouped_features["f0"]
        engineered.extend([
            len(f0[f0 > 0]) / len(f0),  # 有声段比例
            np.std(np.diff(f0[f0 > 0])), # 音高变化率
            # ... 更多节奏特征
        ])
        
        # 3. 情绪场
        voice_q = grouped_features["voice_quality"]
        engineered.extend([
            np.mean(voice_q[:100]),  # 抖动（jitter）
            np.mean(voice_q[100:200]),  # 闪烁（shimmer）
            # ... 更多音质特征
        ])
        
        return np.array(engineered)
    
    def encode(self, features):
        """编码为气场向量"""
        # 标准化
        normalized = self.scaler.transform(features.reshape(1, -1))
        
        # ONNX推理
        input_name = self.encoder.get_inputs()[0].name
        aura_vector = self.encoder.run(
            None, 
            {input_name: normalized.astype(np.float32)}
        )[0]
        
        return aura_vector.flatten()

# 气场匹配相似度计算
def calculate_aura_similarity(aura1: np.ndarray, aura2: np.ndarray) -> float:
    """
    计算两个气场向量的相似度
    
    使用余弦相似度，但加入"互补性"考量：
    - 某些维度相似更好（如价值观表达方式）
    - 某些维度互补更好（如主导性-顺从性）
    """
    # 基础余弦相似度
    base_similarity = np.dot(aura1, aura2) / (
        np.linalg.norm(aura1) * np.linalg.norm(aura2)
    )
    
    # 互补性加成
    complement_dims = [10, 11, 12]  # 假设这些维度代表主导性等
    complement_score = 0
    for dim in complement_dims:
        # 这两个维度差异大反而好
        diff = abs(aura1[dim] - aura2[dim])
        complement_score += min(diff, 0.5)  # 差异有上限
    
    # 加权融合
    final_score = 0.7 * base_similarity + 0.3 * complement_score
    
    return float(final_score)
```

#### 3.3.3 气场向量到结构化标签

```python
class AuraInterpreter:
    """将气场向量解释为人类可理解的标签"""
    
    DIMENSION_LABELS = {
        # 维度索引: (正面标签, 负面标签)
        0: ("声音洪亮", "声音柔和"),
        1: ("表达有力", "表达温和"),
        2: ("语速快", "语速慢"),
        3: ("情绪丰富", "情绪平稳"),
        4: ("自信表达", "谨慎表达"),
        5: ("主导性强", "配合度高"),
        # ... 更多维度
    }
    
    def interpret(self, aura_vector: np.ndarray) -> dict:
        """将128维向量转为可读标签"""
        labels = {}
        
        for dim, (pos_label, neg_label) in self.DIMENSION_LABELS.items():
            value = aura_vector[dim]
            if value > 0.3:
                labels[dim] = {"label": pos_label, "intensity": value}
            elif value < -0.3:
                labels[dim] = {"label": neg_label, "intensity": -value}
        
        return labels
    
    def generate_aura_description(self, aura_vector: np.ndarray) -> str:
        """生成气场描述文本"""
        labels = self.interpret(aura_vector)
        top_traits = sorted(
            labels.items(), 
            key=lambda x: x[1]["intensity"], 
            reverse=True
        )[:5]
        
        description = "TA的沟通风格："
        for dim, info in top_traits:
            description += f"{info['label']}、"
        
        return description.rstrip("、")
```

### 3.4 AI初筛 + 心理咨询师标注 双层架构

#### 3.4.1 标注平台设计

```
┌─────────────────────────────────────────────────────────────┐
│                    标注平台架构                              │
│                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │  标注队列   │   │  标注界面   │   │  质检模块   │       │
│  │             │   │             │   │             │       │
│  │ • AI预标注  │→  │ • 音频播放  │→  │ • 一致性    │       │
│  │ • 优先级    │   │ • 波形显示  │   │ • 复核      │       │
│  │ • 分配策略  │   │ • 标签选择  │   │ • 仲裁      │       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                 │
│                     标注数据库                               │
└─────────────────────────────────────────────────────────────┘
```

#### 3.4.2 AI辅助标注

```python
class AIAssistedLabeling:
    """AI辅助标注系统"""
    
    async def pre_label(self, audio_segment, transcript):
        """AI预标注，标注师只需确认或微调"""
        
        # 1. AI分析结果
        aura_vector = await self.emotion_agent.analyze(audio_segment)
        ai_labels = self.aura_interpreter.interpret(aura_vector)
        
        # 2. 置信度评估
        confidence = self.calculate_confidence(aura_vector)
        
        # 3. 不确定项标记
        uncertain_items = [
            dim for dim, info in ai_labels.items()
            if info["intensity"] < 0.4  # 低置信度
        ]
        
        return {
            "pre_labels": ai_labels,
            "confidence": confidence,
            "uncertain_items": uncertain_items,
            "suggested_focus": uncertain_items  # 提示标注师重点关注
        }
    
    async def smart_assignment(self, sample, annotators):
        """智能分配 - 根据样本特点和标注师专长"""
        
        # 样本难度评估
        difficulty = self.estimate_difficulty(sample)
        
        # 匹配最合适的标注师
        best_match = max(
            annotators,
            key=lambda a: self.expertise_match(a.expertise, sample.tags)
        )
        
        return best_match.id
```

#### 3.4.3 标注数据反哺模型

```python
class FeedbackLoop:
    """标注数据反哺系统"""
    
    async def update_model(self):
        """定期用新标注数据更新模型"""
        
        # 1. 收集新标注数据
        new_labels = await self.fetch_new_labels(since="last_update")
        
        # 2. 计算AI预测与人工标注的差异
        ai_predictions = [l.ai_label for l in new_labels]
        human_labels = [l.human_label for l in new_labels]
        
        accuracy = self.calculate_accuracy(ai_predictions, human_labels)
        
        # 3. 微调轻量编码器
        if accuracy < 0.85:  # 准确率下降阈值
            await self.fine_tune_encoder(new_labels)
        
        # 4. 更新标签解释规则
        await self.update_interpretation_rules(new_labels)
        
        # 5. 记录版本
        await self.log_model_version(accuracy, len(new_labels))
```

---

## 4. 轻量化与可扩展设计

### 4.1 MVP阶段（0-3个月）

**目标**：验证核心价值，最小化工程成本

#### 架构简化

```
┌─────────────────────────────────────────┐
│            单体应用架构                  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │        FastAPI 服务              │   │
│  │  • WebSocket 端点                │   │
│  │  • Agent 逻辑（进程内调用）       │   │
│  │  • 定时任务                      │   │
│  └─────────────────────────────────┘   │
│              │                          │
│  ┌──────────┴──────────┐               │
│  │                     │               │
│  ▼                     ▼               │
│ PostgreSQL          Redis              │
│ (用户+画像+标注)    (会话+队列)         │
└─────────────────────────────────────────┘
```

#### Agent简化

| MVP Agent | 职责 | 简化方式 |
|-----------|------|----------|
| 主控Agent | 对话+调度 | 单一LLM调用，无复杂编排 |
| 情感Agent | 气场分析 | 规则+预训练模型（不微调） |
| 匹配Agent | 推荐 | 简单余弦相似度，无混合排序 |

#### 数据存储

```sql
-- MVP简化：关系型存储，不用向量库
CREATE TABLE users (
    id UUID PRIMARY KEY,
    aura_vector FLOAT[128],  -- PostgreSQL数组存储
    profile JSONB,
    created_at TIMESTAMP
);

-- 匹配时用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE INDEX ON users USING ivfflat (aura_vector vector_cosine_ops);
```

### 4.2 规模化阶段（3-12个月）

**目标**：支撑10万+DAU，毫秒级匹配

#### 微服务化

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                          │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ 语音服务    │ │ Agent服务   │ │ 匹配服务    │ │ 用户服务    │
│             │ │             │ │             │ │             │
│ • ASR/TTS   │ │ • Agent容器 │ │ • 向量检索  │ │ • 画像管理  │
│ • VAD       │ │ • 状态管理  │ │ • 实时排序  │ │ • 认证授权  │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Kafka 消息队列   │
                    └───────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Milvus集群  │      │ PostgreSQL  │      │ Redis集群   │
│ (向量检索)  │      │ (关系数据)  │      │ (缓存/会话) │
└─────────────┘      └─────────────┘      └─────────────┘
```

#### Agent容器化

```yaml
# Agent服务部署配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-service
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: orchestrator-agent
        image: registry/agent-orchestrator:v1.0
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
      - name: emotion-agent
        image: registry/agent-emotion:v1.0
        resources:
          requests:
            memory: "256Mi"  # 轻量模型
            cpu: "250m"
      # ... 其他Agent
```

#### 实时特征平台

```python
# 实时特征计算流水线
class RealtimeFeaturePipeline:
    """支撑实时匹配的特征平台"""
    
    def __init__(self):
        self.feature_store = RedisFeatureStore()
        self.stream_processor = FlinkProcessor()
    
    async def update_user_features(self, user_id, interaction_data):
        """用户每次交互后更新特征"""
        
        # 1. 增量更新气场向量（指数移动平均）
        new_aura = interaction_data["aura_vector"]
        old_aura = await self.feature_store.get(f"aura:{user_id}")
        
        updated_aura = 0.7 * old_aura + 0.3 * new_aura
        await self.feature_store.set(f"aura:{user_id}", updated_aura)
        
        # 2. 更新在线特征
        features = {
            "last_active": now(),
            "interaction_count": increment(),
            "aura_drift": cosine_distance(old_aura, new_aura)
        }
        await self.feature_store.hmset(f"features:{user_id}", features)
        
        # 3. 触发异步重索引
        await self.trigger_reindex(user_id, updated_aura)
```

---

## 5. 数据闭环与交付收费支撑

### 5.1 交付成功的数据埋点

#### 关键事件定义

```python
class DeliveryEvents:
    """交付事件定义"""
    
    EVENTS = {
        # 匹配阶段
        "match_shown": {
            "description": "向用户展示匹配结果",
            "params": ["match_id", "user_id", "score", "position"]
        },
        "match_clicked": {
            "description": "用户点击查看匹配详情",
            "params": ["match_id", "user_id", "dwell_time"]
        },
        "match_accepted": {
            "description": "用户接受匹配",
            "params": ["match_id", "user_id", "match_user_id"]
        },
        "match_rejected": {
            "description": "用户拒绝匹配",
            "params": ["match_id", "user_id", "reason"]
        },
        
        # 约会阶段
        "date_suggested": {
            "description": "AI建议约会",
            "params": ["date_id", "match_id", "venue", "time"]
        },
        "date_confirmed": {
            "description": "约会确认（双方同意）",
            "params": ["date_id", "user_ids", "venue", "time"]
        },
        "date_reminder_sent": {
            "description": "约会提醒发送",
            "params": ["date_id", "channel"]
        },
        "date_completed": {
            "description": "约会完成（通过地理位置/反馈确认）",
            "params": ["date_id", "verification_method"]
        },
        
        # 付费阶段
        "order_created": {
            "description": "订单创建（订餐/订票）",
            "params": ["order_id", "date_id", "amount", "items"]
        },
        "order_paid": {
            "description": "订单支付成功",
            "params": ["order_id", "amount", "payment_method"]
        },
        "order_delivered": {
            "description": "服务交付完成",
            "params": ["order_id", "delivery_time"]
        }
    }
```

#### 埋点实现

```python
class AnalyticsTracker:
    """埋点追踪器"""
    
    async def track(self, event_name: str, params: dict):
        """记录事件"""
        event = {
            "event": event_name,
            "params": params,
            "timestamp": time.time(),
            "session_id": self.get_session_id(),
            "user_id": self.get_user_id()
        }
        
        # 1. 实时发送到Kafka
        await self.kafka_producer.send("analytics_events", event)
        
        # 2. 本地缓存（防丢失）
        await self.local_buffer.append(event)
        
        # 3. 更新实时指标
        await self.update_realtime_metrics(event_name)
    
    async def track_date_completion(self, date_id: str):
        """约会完成追踪 - 核心交付指标"""
        
        # 1. 获取约会信息
        date_info = await self.get_date_info(date_id)
        
        # 2. 验证完成（多种方式）
        verified = False
        verification_method = None
        
        # 方式1：双方确认
        if await self.both_confirmed(date_id):
            verified = True
            verification_method = "both_confirmed"
        
        # 方式2：地理位置签到
        elif await self.location_check(date_id):
            verified = True
            verification_method = "location_verified"
        
        # 方式3：照片上传
        elif await self.photo_uploaded(date_id):
            verified = True
            verification_method = "photo_evidence"
        
        if verified:
            await self.track("date_completed", {
                "date_id": date_id,
                "verification_method": verification_method,
                "match_score": date_info["match_score"],
                "time_to_date": date_info["time_to_date"]
            })
            
            # 触发付费
            await self.trigger_billing(date_id)
```

### 5.2 数据飞轮

```
┌─────────────────────────────────────────────────────────────┐
│                        数据飞轮                              │
│                                                              │
│    语音交互 ──→ 情感/语义分析 ──→ 匹配推荐 ──→ 线下交付      │
│        ↑                                              │      │
│        │                                              │      │
│        └──────────── 结果反馈 ←─────────────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘

详细流程：

1. 语音交互
   - 记录：音频片段、时长、对话内容
   - 产出：原始语音数据

2. 情感/语义分析
   - 提取：气场向量、意图标签、情绪状态
   - 更新：用户画像、特征库

3. 匹配推荐
   - 计算：匹配分数、排序
   - 记录：推荐列表、用户选择

4. 线下交付
   - 追踪：约会执行、消费行为
   - 验证：完成确认、支付记录

5. 结果反馈
   - 收集：用户满意度、后续发展
   - 标注：成功案例、失败案例
   - 反哺：模型优化、规则调整
```

#### 反馈收集机制

```python
class FeedbackCollector:
    """反馈收集系统"""
    
    async def collect_implicit_feedback(self, user_id, match_id):
        """隐式反馈（用户行为）"""
        
        behavior = await self.analyze_behavior(user_id, match_id)
        
        return {
            "view_duration": behavior["dwell_time"],  # 查看时长
            "action_sequence": behavior["actions"],   # 行为序列
            "response_speed": behavior["response_time"],  # 响应速度
            "engagement_score": self.calculate_engagement(behavior)
        }
    
    async def collect_explicit_feedback(self, date_id):
        """显式反馈（主动评价）"""
        
        # 约会后的问卷
        survey = await self.send_survey(date_id, questions=[
            "对TA的第一印象如何？（1-5分）",
            "对话氛围是否舒适？（1-5分）",
            "是否愿意继续了解？（是/否/不确定）",
            "AI的匹配准确度如何？（1-5分）"
        ])
        
        return survey.responses
    
    async def track_long_term_outcome(self, match_id):
        """长期结果追踪"""
        
        # 持续追踪：
        # - 是否有第二次约会
        # - 是否建立恋爱关系
        # - 关系持续时间
        
        outcome = await self.check_relationship_status(match_id)
        
        return {
            "second_date": outcome["has_second_date"],
            "relationship_status": outcome["status"],
            "duration_days": outcome["duration"],
            "success_level": self.classify_success(outcome)
        }
```

#### 模型反哺闭环

```python
class ModelFeedbackLoop:
    """模型持续优化闭环"""
    
    async def run_daily_update(self):
        """每日模型更新任务"""
        
        # 1. 收集过去24h的反馈数据
        feedback_data = await self.fetch_recent_feedback()
        
        # 2. 分析成功/失败模式
        patterns = await self.analyze_patterns(feedback_data)
        
        # 3. 更新匹配权重
        if patterns["success_patterns"]:
            await self.update_match_weights(patterns["success_patterns"])
        
        # 4. 生成新训练样本
        training_samples = self.generate_training_data(feedback_data)
        await self.append_to_training_pool(training_samples)
        
        # 5. 触发微调（如果样本足够）
        if len(training_samples) > 1000:
            await self.trigger_fine_tuning()
        
        # 6. 评估新模型
        if await self.new_model_available():
            metrics = await self.evaluate_model()
            if metrics["accuracy"] > self.current_accuracy:
                await self.deploy_new_model()
```

### 5.3 按效果付费支撑

```python
class BillingService:
    """按效果付费系统"""
    
    BILLING_RULES = {
        "date_confirmed": {
            "amount": 29.9,  # 基础约会费
            "description": "约会确认后收取"
        },
        "date_completed": {
            "amount": 99.9,  # 成功交付费
            "description": "约会完成验证后收取"
        },
        "relationship_30days": {
            "amount": 299.9,  # 长期成功费
            "description": "建立关系满30天后收取"
        }
    }
    
    async def process_billing(self, event_type: str, event_data: dict):
        """处理付费事件"""
        
        if event_type not in self.BILLING_RULES:
            return
        
        rule = self.BILLING_RULES[event_type]
        
        # 1. 创建账单
        bill = await self.create_bill(
            user_id=event_data["user_id"],
            amount=rule["amount"],
            description=rule["description"],
            event_id=event_data["event_id"]
        )
        
        # 2. 发送支付请求
        payment_url = await self.request_payment(bill)
        
        # 3. 记录到分析系统
        await self.track_billing_event(bill, event_type)
        
        return payment_url
```

---

## 6. 快速体验方案

### 6.1 MVP核心功能Demo

**目标**：2周内可体验的核心流程

```
1. 用户注册 → 2分钟语音引导对话 → 生成气场画像
2. 查看匹配 → 展示3个最匹配用户（带气场解释）
3. 模拟约会 → AI生成约会建议
```

### 6.2 技术实现（最小化）

```python
# mvp_main.py - 核心Demo入口
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def demo_page():
    """体验页面"""
    return HTMLResponse("""
    <html>
    <head><title>AI语音匹配Demo</title></head>
    <body>
        <h1>AI语音匹配体验</h1>
        <button onclick="startChat()">开始语音对话</button>
        <div id="result"></div>
        <script>
        // WebSocket连接语音服务
        let ws = new WebSocket('ws://localhost:8000/voice');
        
        function startChat() {
            // 获取麦克风权限
            navigator.mediaDevices.getUserMedia({audio: true})
                .then(stream => startStreaming(stream));
        }
        </script>
    </body>
    </html>
    """)

@app.websocket("/voice")
async def voice_endpoint(websocket: WebSocket):
    """语音交互入口"""
    await websocket.accept()
    
    # MVP简化：直接调用单个LLM
    while True:
        # 接收音频
        audio_data = await websocket.receive_bytes()
        
        # ASR转文本
        transcript = await asr_service.transcribe(audio_data)
        
        # LLM生成回复
        response = await llm.chat(
            messages=[
                {"role": "system", "content": "你是婚恋匹配助手..."},
                {"role": "user", "content": transcript}
            ]
        )
        
        # TTS转语音
        audio_response = await tts_service.synthesize(response)
        
        # 返回音频
        await websocket.send_bytes(audio_response)
```

### 6.3 部署脚本

```bash
#!/bin/bash
# quick_start.sh - 一键启动Demo

# 1. 安装依赖
pip install fastapi uvicorn websockets openai redis

# 2. 配置环境变量
export OPENAI_API_KEY="your-key"
export ASR_API_KEY="your-asr-key"
export TTS_API_KEY="your-tts-key"

# 3. 启动服务
python mvp_main.py

# 访问 http://localhost:8000 开始体验
```

---

## 附录：关键技术指标

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 端到端延迟 | <800ms | 用户说完到AI开始回复 |
| ASR准确率 | >95% | 人工抽检 |
| 气场向量维度 | 128维 | 平衡精度和效率 |
| 匹配准确率 | >70% | 用户反馈率 |
| 标注一致性 | >85% | 双标注Kappa系数 |
| 交付成功率 | >60% | 约会完成/匹配数 |

---

**文档版本**: v1.0  
**更新日期**: 2026-03-01  
**作者**: AI技术架构师
