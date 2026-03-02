"""
AI语音匹配平台 - MVP Demo

完整演示应用，集成ASR/TTS/LLM/匹配引擎
"""
import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from config_loader import config
from providers import XunfeiASRClient, XunfeiTTSClient, KimiLLMClient
from services import SimpleMatcher
from core.base import ASRProvider, TTSProvider, LLMProvider, MatchingEngine


# 初始化FastAPI
app = FastAPI(
    title="AI语音匹配平台",
    description="基于语音的智能匹配系统",
    version="1.0.0"
)


# ================== 服务初始化 ==================

def init_asr() -> ASRProvider:
    """初始化ASR服务"""
    asr_config = config.xunfei_asr
    return XunfeiASRClient(
        appid=asr_config['appid'],
        api_key=asr_config['api_key'],
        api_secret=asr_config['api_secret']
    )


def init_tts() -> TTSProvider:
    """初始化TTS服务"""
    tts_config = config.xunfei_tts
    return XunfeiTTSClient(
        appid=tts_config['appid'],
        api_key=tts_config['api_key'],
        api_secret=tts_config['api_secret']
    )


def init_llm() -> LLMProvider:
    """初始化LLM服务"""
    kimi_config = config.kimi
    return KimiLLMClient(
        api_key=kimi_config['api_key'],
        base_url=kimi_config['base_url'],
        model=kimi_config['model']
    )


def init_matcher() -> MatchingEngine:
    """初始化匹配引擎"""
    return SimpleMatcher()


# 全局服务实例
asr_service = init_asr()
tts_service = init_tts()
llm_service = init_llm()
matcher_service = init_matcher()


# ================== 对话管理器 ==================

class ConversationManager:
    """对话管理器"""
    
    def __init__(self):
        self.conversations = {}  # session_id -> 对话历史
        self.profiles = {}  # session_id -> 用户画像
    
    def get_history(self, session_id: str) -> list:
        """获取对话历史"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        return self.conversations[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到历史"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": role,
            "content": content
        })
    
    def update_profile(self, session_id: str, profile: dict):
        """更新用户画像"""
        self.profiles[session_id] = profile


conversation_manager = ConversationManager()


# ================== API路由 ==================

@app.get("/")
async def root():
    """首页 - Web UI"""
    return HTMLResponse(content=get_demo_html())


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "services": {
            "asr": asr_service.name,
            "tts": tts_service.name,
            "llm": llm_service.name,
            "matcher": matcher_service.name
        }
    }


@app.post("/api/match")
async def match_users(user_profile: dict):
    """
    匹配接口
    
    Args:
        user_profile: 用户画像
    
    Returns:
        匹配结果
    """
    # 分析用户特征
    user_features = await matcher_service.analyze_profile(user_profile)
    
    # 模拟候选人（实际应从数据库获取）
    candidates = [
        {
            "user_id": "user_001",
            "age": 26,
            "interests": ["音乐", "电影", "旅游"],
            "interest_vector": [1, 1, 0, 1, 0, 0, 0, 0, 0, 0],
            "profile": {"name": "小明", "bio": "喜欢音乐和旅行"}
        },
        {
            "user_id": "user_002",
            "age": 28,
            "interests": ["运动", "美食", "摄影"],
            "interest_vector": [0, 0, 1, 0, 1, 0, 0, 1, 0, 0],
            "profile": {"name": "小红", "bio": "热爱运动和美食"}
        }
    ]
    
    # 执行匹配
    matches = await matcher_service.find_matches(user_features, candidates, top_k=3)
    
    return {
        "success": True,
        "matches": matches
    }


# ================== WebSocket对话 ==================

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket实时对话
    
    协议：
    - 客户端 -> 服务端: {"type": "text", "content": "..."}
    - 客户端 -> 服务端: {"type": "audio", "data": "base64编码的音频"}
    - 服务端 -> 客户端: {"type": "text", "content": "..."}
    - 服务端 -> 客户端: {"type": "audio", "data": "base64编码的音频"}
    """
    await websocket.accept()
    logger.info(f"✅ WebSocket连接建立: {session_id}")
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            message_type = data.get("type")
            logger.info(f"📨 收到消息 [{session_id}]: type={message_type}")
            
            if message_type == "text":
                # 文本对话
                user_text = data.get("content", "")
                logger.info(f"💬 用户消息: {user_text[:50]}...")
                
                try:
                    # 获取对话历史
                    history = conversation_manager.get_history(session_id)
                    logger.info(f"📚 对话历史长度: {len(history)}")
                    
                    # 构建系统提示
                    system_prompt = """你是VoiceVibe语音匹配助手。
你的任务是通过对话了解用户的兴趣、性格和偏好，帮助他们找到合适的匹配对象。

对话风格：
- 亲切自然，像朋友聊天
- 逐步了解用户的兴趣、爱好、价值观
- 给予积极的反馈和建议
- 简洁回复，不要太长

当前目标：了解用户的基本信息和兴趣爱好。"""
                    
                    logger.info("🤖 调用Kimi LLM...")
                    # 调用LLM
                    response_text = await llm_service.chat_with_system(
                        user_message=user_text,
                        system_prompt=system_prompt,
                        conversation_history=history,
                        temperature=0.8
                    )
                    logger.info(f"✨ LLM回复: {response_text[:100]}...")
                    
                    # 更新对话历史
                    conversation_manager.add_message(session_id, "user", user_text)
                    conversation_manager.add_message(session_id, "assistant", response_text)
                    
                    # 检查连接是否仍然活跃
                    try:
                        # 返回文本回复
                        await websocket.send_json({
                            "type": "text",
                            "content": response_text
                        })
                        logger.info("✅ 文本回复已发送")
                    except Exception as send_error:
                        logger.warning(f"⚠️ 发送失败，连接可能已关闭: {send_error}")
                        break
                    
                    # 跳过TTS（避免超时）
                    logger.info("⏭️ 跳过语音生成（避免超时）")
                
                except Exception as e:
                    logger.error(f"❌ LLM调用失败: {e}", exc_info=True)
                    # 检查连接再发送错误
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "content": f"抱歉，出现错误: {str(e)}"
                        })
                    except:
                        logger.error("无法发送错误消息，连接已关闭")
                        break
            
            elif message_type == "audio":
                # 语音对话
                import base64
                
                audio_base64 = data.get("data", "")
                audio_data = base64.b64decode(audio_base64)
                logger.info(f"🎤 收到音频: {len(audio_data)} bytes")
                
                try:
                    # ASR识别
                    logger.info("🔇 语音识别中...")
                    transcribed_text = await asr_service.transcribe(audio_data)
                    logger.info(f"✅ 识别结果: {transcribed_text}")
                    
                    # 通知客户端识别结果
                    await websocket.send_json({
                        "type": "transcript",
                        "content": transcribed_text
                    })
                except Exception as e:
                    logger.error(f"❌ ASR错误: {e}", exc_info=True)
                    
                    # 发送友好的错误提示
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "content": "⚠️ 语音识别服务暂时不可用。请使用文字输入，或稍后再试。"
                        })
                    except:
                        logger.error("无法发送错误消息")
                        break
    
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket断开: {session_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket错误: {e}", exc_info=True)
        await websocket.close()


# ================== Web UI ==================

def get_demo_html() -> str:
    """返回Demo页面HTML"""
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI语音匹配平台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 90%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 16px;
        }
        .chat-box {
            height: 400px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            overflow-y: auto;
            margin-bottom: 20px;
            background: #f9f9f9;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
        }
        .user {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .assistant {
            background: white;
            border: 1px solid #e0e0e0;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        input, button {
            padding: 12px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            font-size: 16px;
        }
        input {
            flex: 1;
            outline: none;
        }
        input:focus {
            border-color: #667eea;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
            padding: 12px 24px;
            transition: all 0.3s;
        }
        button:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .voice-btn {
            background: #ff6b6b;
            min-width: 100px;
        }
        .voice-btn:hover {
            background: #ee5a5a;
        }
        .voice-btn.recording {
            background: #f44336;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        .status {
            text-align: center;
            color: #999;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 VoiceVibe - AI语音匹配平台</h1>
        <p class="subtitle">基于语音的智能匹配系统 | <span style="color: #ff6b6b;">⚠️ 语音识别服务维护中，请使用文字输入</span></p>
        
        <div class="chat-box" id="chatBox">
            <div class="message assistant">
                你好！我是AI匹配助手。告诉我你的兴趣爱好，我来帮你找到合适的伙伴！
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="userInput" placeholder="输入消息..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">发送</button>
            <button id="voiceBtn" class="voice-btn" onclick="toggleRecording()" disabled title="语音识别服务维护中">🎤 录音</button>
        </div>
        
        <p class="status" id="status">连接中...</p>
    </div>

    <script>
        const sessionId = 'demo_' + Date.now();
        let ws = null;
        let mediaRecorder = null;
        let audioChunks = [];
        let isRecording = false;
        
        function connect() {
            ws = new WebSocket(`ws://${location.host}/ws/chat/${sessionId}`);
            
            ws.onopen = () => {
                document.getElementById('status').textContent = '已连接';
                document.getElementById('status').style.color = '#4caf50';
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'text') {
                    addMessage('assistant', data.content);
                } else if (data.type === 'transcript') {
                    addMessage('user', data.content);
                } else if (data.type === 'audio') {
                    // 播放语音回复
                    playAudio(data.data);
                }
            };
            
            ws.onerror = (error) => {
                document.getElementById('status').textContent = '连接错误';
                document.getElementById('status').style.color = '#f44336';
            };
            
            ws.onclose = () => {
                document.getElementById('status').textContent = '已断开';
                document.getElementById('status').style.color = '#ff9800';
            };
        }
        
        function addMessage(role, content) {
            const chatBox = document.getElementById('chatBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            messageDiv.textContent = content;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // 显示用户消息
            addMessage('user', message);
            
            // 发送到服务器
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'text',
                    content: message
                }));
            }
            
            input.value = '';
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        // 语音录制功能
        async function toggleRecording() {
            const voiceBtn = document.getElementById('voiceBtn');
            
            if (!isRecording) {
                // 开始录音
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const reader = new FileReader();
                        
                        reader.onloadend = () => {
                            const base64Audio = reader.result.split(',')[1];
                            
                            // 发送音频到服务器
                            if (ws && ws.readyState === WebSocket.OPEN) {
                                ws.send(JSON.stringify({
                                    type: 'audio',
                                    data: base64Audio
                                }));
                                
                                document.getElementById('status').textContent = '识别中...';
                            }
                        };
                        
                        reader.readAsDataURL(audioBlob);
                        
                        // 停止所有音轨
                        stream.getTracks().forEach(track => track.stop());
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    voiceBtn.textContent = '⏹️ 停止';
                    voiceBtn.classList.add('recording');
                    document.getElementById('status').textContent = '录音中...';
                    
                } catch (error) {
                    console.error('录音失败:', error);
                    alert('无法访问麦克风，请检查权限设置');
                }
            } else {
                // 停止录音
                if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                    mediaRecorder.stop();
                    isRecording = false;
                    voiceBtn.textContent = '🎤 录音';
                    voiceBtn.classList.remove('recording');
                }
            }
        }
        
        // 播放语音
        function playAudio(base64Audio) {
            const audio = new Audio('data:audio/wav;base64,' + base64Audio);
            audio.play().catch(error => console.error('播放失败:', error));
        }
        
        // 初始化连接
        connect();
    </script>
</body>
</html>
    """


# ================== 启动 ==================

if __name__ == "__main__":
    print("=" * 60)
    print("  AI语音匹配平台 - MVP Demo")
    print("=" * 60)
    print(f"  ASR服务: {asr_service.name}")
    print(f"  TTS服务: {tts_service.name}")
    print(f"  LLM服务: {llm_service.name}")
    print(f"  匹配引擎: {matcher_service.name}")
    print("=" * 60)
    print("  访问: http://localhost:8000")
    print("  API文档: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
