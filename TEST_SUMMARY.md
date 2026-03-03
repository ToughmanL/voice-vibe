# 🎉 科大讯飞 ASR 测试工具完成

## 📦 交付内容

我已经为你创建了一套完整的科大讯飞 ASR 测试工具套件。

### 核心文件

#### 1️⃣ 测试工具

| 文件 | 用途 | 使用场景 |
|------|------|---------|
| `generate_test_audio.py` | 生成测试音频 | 首次使用、缺少测试音频时 |
| `quick_test.py` | 快速验证连接 | 开发调试、验证服务可用性 |
| `test_asr_audio.py` | 完整测试工具 | 正式测试、集成测试 |
| `diagnose_xunfei.py` | 诊断工具 | 排查连接问题 |

#### 2️⃣ 文档

| 文件 | 内容 |
|------|------|
| `TEST_README.md` | 完整使用指南 |
| `TEST_CHANGELOG.md` | 更新日志和功能说明 |

#### 3️⃣ 测试音频

```
test_audio/
├── silence_1s.wav          # 1秒静音
├── silence_3s.wav          # 3秒静音
├── tone_440hz_2s.wav       # 440Hz单音
├── tone_880hz_2s.wav       # 880Hz单音
└── real/                   # 真实语音（自行录制）
```

### 🔧 修复的问题

#### ASR 客户端修复 (`src/providers/xunfei/asr_client.py`)

1. **WebSocket 参数错误**
   ```python
   # 修复前
   self.ws = await websockets.connect(url)
   
   # 修复后
   self.ws = await websockets.connect(
       url,
       open_timeout=30,
       close_timeout=10
   )
   ```

2. **更换推荐主机**
   ```python
   # 修复前
   host = "ws-api.xfyun.cn"
   
   # 修复后
   host = "iat-api.xfyun.cn"  # 讯飞推荐的主机
   ```

## 🚀 快速开始

### 方式一：快速验证（推荐）

```bash
# 1. 生成测试音频（首次使用）
cd /Users/jack/.openclaw-autoclaw/workspace/projects/voice-vibe
python3 generate_test_audio.py

# 2. 快速测试
python3 quick_test.py
```

### 方式二：完整测试

```bash
# 运行完整测试套件
python3 test_asr_audio.py

# 查看结果
cat test_results.json
```

### 方式三：诊断问题

```bash
# 如果遇到问题，运行诊断
python3 diagnose_xunfei.py
```

## ⚠️ 重要提示

### 关于频率限制

根据之前的测试，讯飞 API 对频繁请求有限制：

1. **当前状态**：之前测试触发了限制
2. **恢复时间**：建议等待 **30-60 分钟**后再测试
3. **最佳时间**：**明天**再进行测试

### 测试策略

为避免再次触发限制：

1. **使用快速测试**：`quick_test.py` 只进行 2 次请求
2. **控制频率**：测试工具已内置 5 秒间隔
3. **避免重复**：不要频繁运行诊断工具
4. **使用真实音频**：静音音频仅用于验证连接

## 📊 测试流程建议

### 首次测试（明天）

```bash
# 1. 快速验证
python3 quick_test.py

# 如果成功 ✅
# 2. 准备真实语音（录制一段话）
# 3. 保存到 test_audio/real/
# 4. 运行完整测试
python3 test_asr_audio.py
```

### 日常开发

```bash
# 快速验证
python3 quick_test.py

# 如果需要详细信息
python3 diagnose_xunfei.py
```

### 集成测试

```bash
# 完整测试套件
python3 test_asr_audio.py

# 查看结果
cat test_results.json
```

## 🎯 测试音频说明

### 已生成的测试音频

1. **静音音频** (`silence_*.wav`)
   - 用途：测试连接和音频传输
   - 预期结果：空字符串
   - 不消耗配额（无实际语音）

2. **单音音频** (`tone_*.wav`)
   - 用途：测试音频编码
   - 预期结果：空或乱码
   - 不推荐用于识别测试

### 真实语音（需自行准备）

要测试真实语音识别：

1. **录制语音**
   - 软件：Audacity、QuickTime、Voice Memos
   - 格式：16kHz, 16bit, 单声道
   - 内容：清晰的中文语音

2. **保存文件**
   ```bash
   mkdir -p test_audio/real
   # 将录制的 .wav 文件保存到此目录
   ```

3. **运行测试**
   ```bash
   python3 test_asr_audio.py
   ```

## 📈 下一步

### 立即可做

1. ✅ 测试音频已生成
2. ✅ 测试工具已就绪
3. ✅ 代码已修复

### 建议时间线

**今天**：
- ❌ 避免测试（限制未解除）

**明天**：
- ✅ 运行 `quick_test.py` 验证连接
- ✅ 准备真实语音音频
- ✅ 运行 `test_asr_audio.py` 完整测试

**日常使用**：
- ✅ 使用 `quick_test.py` 快速验证
- ✅ 定期运行完整测试
- ✅ 监控 `test_results.json` 中的成功率

## 💡 使用技巧

### 1. 避免频繁测试

```python
# 在 test_asr_audio.py 中调整间隔
self.min_interval = 10  # 增加到 10 秒
```

### 2. 自定义测试

```python
from test_asr_audio import ASRTester

tester = ASRTester()
await tester.test_audio_file("my_audio.wav", "我的测试")
```

### 3. 查看详细日志

所有测试都会输出详细信息，包括：
- 音频格式
- 连接状态
- 识别结果
- 错误信息

## 🔗 相关资源

- **测试工具位置**：`/Users/jack/.openclaw-autoclaw/workspace/projects/voice-vibe/`
- **配置文件**：`config/api_keys.json`
- **测试音频**：`test_audio/`
- **测试结果**：`test_results.json`

## ✅ 检查清单

开始测试前，确认：

- [ ] 等待足够时间（30-60 分钟）
- [ ] 测试音频已生成（`test_audio/` 目录存在）
- [ ] 配置文件正确（`config/api_keys.json`）
- [ ] 网络连接正常
- [ ] 未频繁运行测试

---

**准备好测试了吗？明天运行 `python3 quick_test.py` 开始吧！** 🚀
