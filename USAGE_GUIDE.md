# AI 语音匹配平台 - 完整使用流程

## 🎯 项目核心功能

这个平台主要功能是：**通过语音与 AI 对话，并进行用户匹配**

### 完整流程

```
用户输入（语音/文字）
    ↓
语音识别 (ASR) → 转成文字
    ↓
智能对话 (LLM) → 生成回复
    ↓
语音合成 (TTS) → 转成语音
    ↓
智能匹配 → 找到合适的伙伴
```

---

## 📋 三种使用方式

### 方式一：浏览器界面（最简单）✅ 推荐

#### 步骤：

1. **打开浏览器**
   ```
   访问: http://localhost:8000
   ```

2. **文字对话**（推荐先用这个测试）
   - 在输入框输入："你好"
   - 点击"发送"
   - 查看 AI 回复

3. **语音对话**（需要麦克风权限）
   - 点击 🎤 录音按钮
   - 说话（如："介绍一下你自己"）
   - 再次点击停止录音
   - 等待识别和回复

4. **查看匹配**（通过对话触发）
   - 说："我想找志同道合的朋友"
   - AI 会分析你的兴趣
   - 返回匹配的用户列表

---

### 方式二：WebSocket 测试（开发者）

#### 连接地址：
```
ws://localhost:8000/ws/chat/<session_id>
```

#### 完整示例代码：

```python
import asyncio
import websockets
import json

async def test_chat():
    # 1. 连接 WebSocket
    ws_url = "ws://localhost:8000/ws/chat/test_session_001"
    ws = await websockets.connect(ws_url, open_timeout=10)

    print("✅ 已连接")

    # 2. 发送文本消息
    message = {
        "type": "text",
        "content": "你好，我想找喜欢编程的朋友"
    }
    await ws.send(json.dumps(message))
    print(f"📤 发送: {message['content']}")

    # 3. 接收回复
    response = await ws.recv()
    data = json.loads(response)
    print(f"📥 收到: {data}")

    # 4. 关闭连接
    await ws.close()
    print("✅ 已关闭")

# 运行
asyncio.run(test_chat())
```

---

### 方式三：REST API（集成到其他系统）

#### 1. 健康检查
```bash
curl http://localhost:8000/health
```

#### 2. 匹配接口
```bash
curl -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "my_user",
    "profile": {
      "age": 25,
      "gender": "male",
      "interests": ["coding", "music"],
      "bio": "程序员"
    },
    "text": "你好"
  }'
```

---

## ✅ 完整测试流程

### 第一步：验证服务启动

```bash
# 健康检查
curl http://localhost:8000/health

# 预期结果
{
  "status": "ok",
  "services": {
    "asr": "Xunfei ASR",
    "tts": "Xunfei TTS",
    "llm": "Kimi LLM",
    "matcher": "Simple Matcher"
  }
}
```

### 第二步：测试文字对话

1. 打开浏览器：http://localhost:8000
2. 输入："你好，介绍一下你自己"
3. 点击发送
4. 等待 AI 回复（可能需要几秒）
5. ✅ 成功标志：看到 AI 的回复文字

### 第三步：测试语音输入（可选）

1. 点击 🎤 录音按钮
2. 允许麦克风权限
3. 说话："你好"
4. 点击停止
5. 等待识别
6. ✅ 成功标志：看到识别的文字

### 第四步：测试匹配功能

1. 在对话框输入："我想找志同道合的朋友"
2. 等待 AI 分析和匹配
3. ✅ 成功标志：看到匹配的用户列表

---

## 🐛 常见问题

### 1. 页面打不开

**检查**:
```bash
# 查看进程
ps aux | grep demo.py

# 重启服务
./start.sh
```

### 2. AI 不回复

**可能原因**:
- Kimi API 配额用完
- 网络问题
- 请求超时

**解决**:
```bash
# 查看日志
tail -f nohup.out
```

### 3. 语音识别失败

**检查**:
- 麦克风权限是否授予
- 是否有实际语音内容
- 音量是否足够

### 4. 匹配无结果

**原因**: 匹配需要用户数据

**解决**: 在对话中提到你的兴趣和偏好

---

## 📊 验证清单

走通整个流程，确认以下功能：

- [ ] 1. 服务启动成功（访问 http://localhost:8000）
- [ ] 2. 文字对话正常（发送消息，收到回复）
- [ ] 3. LLM 响应正常（AI 能理解并回复）
- [ ] 4. 语音输入正常（可选，需要麦克风）
- [ ] 5. 匹配功能正常（返回匹配结果）

---

## 🎓 核心概念

### 1. ASR（语音识别）
- **作用**: 把语音转成文字
- **提供商**: 科大讯飞
- **特点**: 实时流式识别

### 2. LLM（大语言模型）
- **作用**: 理解对话，生成回复
- **提供商**: Kimi (Moonshot)
- **特点**: 支持上下文记忆

### 3. TTS（语音合成）
- **作用**: 把文字转成语音
- **提供商**: 科大讯飞
- **特点**: 流式合成

### 4. Matcher（匹配引擎）
- **作用**: 根据用户特征匹配
- **算法**: 多维度相似度计算
- **维度**: 年龄、兴趣、性别等

---

## 🚀 快速开始

### 最简单的验证流程：

```bash
# 1. 启动服务
./start.sh

# 2. 等待启动完成（看到 "Uvicorn running"）

# 3. 打开浏览器
# 访问 http://localhost:8000

# 4. 测试对话
# 输入: "你好"
# 点击发送

# 5. 查看回复
# 应该看到 AI 的回复

# ✅ 完成！
```

---

## 📞 获取帮助

如果遇到问题：

1. **查看日志**: `tail -f nohup.out`
2. **检查配置**: `cat config/api_keys.json`
3. **重启服务**: `./start.sh`
4. **健康检查**: `curl http://localhost:8000/health`

---

**现在，让我们一步步走通这个流程！**
