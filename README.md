# 🎵 VoiceVibe - AI语音气场匹配平台

> 基于实时语音交互的智能匹配系统 - 通过AI分析语音气场，找到与你共鸣的人

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ 特性

- 🎤 **实时语音识别** - 基于科大讯飞WebSocket的流式ASR，延迟<500ms
- 🔊 **流式语音合成** - 支持多种音色的TTS，边生成边播放
- 🤖 **智能对话** - 集成Kimi大模型，自然流畅的多轮对话
- 💕 **精准匹配** - 基于语音特征+兴趣爱好的混合匹配算法
- 🌊 **流式处理** - 全链路流式架构，端到端响应<800ms
- 🏗️ **可扩展架构** - 清晰的抽象接口，易于扩展新服务

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ToughmaL/voice-vibe.git
cd voice-vibe
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置API密钥

```bash
# 复制配置模板
cp config/api_keys.example.json config/api_keys.json

# 编辑配置文件，填入你的API密钥
# 需要：
# - 科大讯飞开发者账号（免费）：https://www.xfyun.cn/
# - Kimi API密钥：https://platform.moonshot.cn/
```

配置示例：
```json
{
  "xunfei": {
    "asr": {
      "appid": "你的APPID",
      "api_secret": "你的APISecret",
      "api_key": "你的APIKey"
    },
    "tts": { ... }
  },
  "kimi": {
    "api_key": "你的Kimi API Key"
  }
}
```

### 4. 启动服务

```bash
cd src
python demo.py
```

访问 http://localhost:8000 即可体验！

## 📖 使用指南

### Web界面演示

启动服务后，打开浏览器访问 `http://localhost:8000`，你会看到：

1. **对话界面** - 与AI助手聊天，它会了解你的兴趣和性格
2. **实时语音** - 输入文本，AI会用语音回复（需浏览器支持WebAudio）
3. **智能匹配** - 根据对话内容分析你的特征，推荐合适的伙伴

### API接口

#### 1. 健康检查

```bash
curl http://localhost:8000/health
```

#### 2. 匹配接口

```bash
curl -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "age": 25,
    "gender": "male",
    "interests": ["音乐", "电影", "运动"]
  }'
```

#### 3. WebSocket对话

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/your_session_id');

// 发送文本消息
ws.send(JSON.stringify({
  type: 'text',
  content: '你好'
}));

// 接收回复
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content);
};
```

## 🏗️ 项目架构

```
ai-match-platform/
├── config/                  # 配置文件
│   ├── api_keys.json       # API密钥（不提交到git）
│   └── api_keys.example.json
├── docs/                    # 文档
│   └── TECH_ARCHITECTURE.md
├── src/                     # 源代码
│   ├── core/               # 核心抽象
│   │   └── base.py         # ASR/TTS/LLM/匹配引擎接口
│   ├── providers/          # 服务提供者
│   │   ├── xunfei/        # 科大讯飞
│   │   │   ├── asr_client.py
│   │   │   └── tts_client.py
│   │   └── kimi/          # Kimi LLM
│   │       └── llm_client.py
│   ├── services/           # 业务服务
│   │   └── matcher.py      # 匹配引擎
│   ├── config_loader.py    # 配置加载
│   └── demo.py             # Demo应用
├── tests/                   # 测试
│   ├── test_xunfei_asr.py
│   ├── test_xunfei_tts.py
│   ├── test_kimi_llm.py
│   ├── test_matcher.py
│   └── test_integration.py
├── requirements.txt         # 依赖
├── pytest.ini              # 测试配置
└── README.md               # 本文件
```

### 核心设计

#### 1. 抽象层（`src/core/base.py`）

定义了四个核心接口：
- `ASRProvider` - 语音识别服务
- `TTSProvider` - 语音合成服务
- `LLMProvider` - 大语言模型服务
- `MatchingEngine` - 匹配引擎

**优势**：易于切换服务商，如将Kimi替换为OpenAI只需实现`LLMProvider`接口。

#### 2. 服务提供者（`src/providers/`）

实现具体服务：
- **讯飞ASR** - WebSocket流式识别，支持动态修正
- **讯飞TTS** - 流式合成，支持多种音色
- **Kimi LLM** - 支持流式对话，8K/32K/128K上下文

#### 3. 匹配引擎（`src/services/matcher.py`）

基于特征的相似度匹配：
- 兴趣向量（10维预定义类别）
- 语音特征（气场分析）
- 年龄、性格等多维度

**匹配分数** = 年龄相似度(20%) + 兴趣相似度(40%) + 语音相似度(40%)

## 🧪 测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试

```bash
# 测试ASR
pytest tests/test_xunfei_asr.py -v

# 测试TTS
pytest tests/test_xunfei_tts.py -v

# 测试LLM
pytest tests/test_kimi_llm.py -v

# 测试匹配引擎
pytest tests/test_matcher.py -v
```

### 测试覆盖率

```bash
pytest --cov=src --cov-report=html
# 打开 htmlcov/index.html 查看详细报告
```

## 🔧 高级配置

### 自定义匹配权重

编辑 `src/services/matcher.py`：

```python
async def _calculate_similarity(self, user_features, candidate):
    scores = []
    
    # 调整权重
    scores.append(age_score * 0.3)        # 年龄权重30%
    scores.append(interest_score * 0.5)   # 兴趣权重50%
    scores.append(voice_score * 0.2)      # 语音权重20%
    
    return sum(scores) / len(scores)
```

### 切换LLM服务商

实现`LLMProvider`接口：

```python
from src.core.base import LLMProvider

class OpenAILLMClient(LLMProvider):
    @property
    def name(self) -> str:
        return "OpenAI GPT-4"
    
    async def chat(self, messages, temperature=0.7, **kwargs):
        # 实现OpenAI调用逻辑
        pass
    
    async def stream_chat(self, messages, temperature=0.7, **kwargs):
        # 实现流式调用
        pass
```

### 添加新的语音特征

扩展匹配引擎：

```python
async def analyze_profile(self, profile):
    features = await super().analyze_profile(profile)
    
    # 添加自定义特征
    features["emotion"] = self._analyze_emotion(profile.get("voice"))
    features["energy"] = self._analyze_energy(profile.get("voice"))
    
    return features
```

## 📊 性能指标

在标准配置下（M1 Mac + 家庭网络）：

| 指标 | 数值 |
|------|------|
| ASR延迟（首字） | < 300ms |
| TTS首包延迟 | < 200ms |
| LLM首token延迟 | < 500ms |
| 端到端响应时间 | < 800ms |
| 并发支持 | 100+ 连接 |

## 🗺️ 路线图

### v1.0（当前）
- ✅ 实时语音识别与合成
- ✅ 智能对话
- ✅ 基础匹配算法
- ✅ Web Demo

### v1.1（计划中）
- [ ] 支持音频文件上传
- [ ] 增加更多匹配维度（价值观、生活方式）
- [ ] 用户反馈机制
- [ ] 匹配效果追踪

### v2.0（未来）
- [ ] 多模态匹配（语音+图像）
- [ ] 强化学习优化匹配策略
- [ ] 移动端App
- [ ] 私有化部署方案

## 🤝 贡献

欢迎贡献代码、报告Bug或提出建议！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码规范

- 使用 `black` 格式化代码
- 使用 `flake8` 检查代码质量
- 使用 `mypy` 进行类型检查
- 编写单元测试（覆盖率>80%）

```bash
# 格式化代码
black src/ tests/

# 检查代码
flake8 src/ tests/

# 类型检查
mypy src/
```

## 📝 License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [科大讯飞开放平台](https://www.xfyun.cn/) - 提供语音识别与合成服务
- [Moonshot AI](https://platform.moonshot.cn/) - 提供Kimi大模型API
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Web框架

## 📮 联系方式

- 项目主页: https://github.com/ToughmaL/voice-vibe
- 问题反馈: https://github.com/ToughmaL/voice-vibe/issues
- 邮箱: your.email@example.com

---

⭐ 如果这个项目对你有帮助，请给一个Star！
