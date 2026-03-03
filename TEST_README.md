# 科大讯飞 ASR 测试工具

完整的测试工具套件，用于测试科大讯飞语音识别功能。

## 📁 文件说明

### 测试工具

- **`generate_test_audio.py`** - 生成测试音频文件
- **`test_asr_audio.py`** - 使用本地音频进行完整测试
- **`diagnose_xunfei.py`** - 诊断工具（网络、鉴权、连接测试）

### 测试音频目录

```
test_audio/
├── silence_1s.wav          # 1秒静音音频
├── silence_3s.wav          # 3秒静音音频
├── tone_440hz_2s.wav       # 440Hz单音（2秒）
├── tone_880hz_2s.wav       # 880Hz单音（2秒）
└── real/                   # 真实语音音频（需自行录制）
    ├── sample1.wav
    └── sample2.wav
```

## 🚀 快速开始

### 1. 生成测试音频

```bash
python3 generate_test_audio.py
```

这将生成基础的测试音频文件（静音和单音）。

### 2. 运行测试

```bash
python3 test_asr_audio.py
```

测试将自动：
- 读取配置文件
- 加载测试音频
- 执行语音识别
- 生成测试报告

### 3. 查看结果

测试结果保存在 `test_results.json` 文件中。

## ⚠️ 重要提示

### 频率限制

为避免触发讯飞 API 的频率限制：

1. **最小请求间隔**: 5秒
2. **推荐测试间隔**: 10秒
3. **避免频繁重连**: 使用长连接

测试工具已内置频率控制机制。

### 音频格式要求

- **格式**: WAV
- **采样率**: 16kHz 或 8kHz
- **采样位数**: 16 bit
- **声道数**: 单声道（mono）
- **编码**: PCM

### 真实语音测试

要测试真实语音识别：

1. 使用录音软件录制语音（推荐：Audacity、QuickTime）
2. 设置音频格式：
   - 16kHz 采样率
   - 16 bit 采样深度
   - 单声道
3. 导出为 WAV 格式
4. 保存到 `test_audio/real/` 目录
5. 运行 `test_asr_audio.py`

## 🔧 高级用法

### 调整频率限制

在 `test_asr_audio.py` 中修改：

```python
self.min_interval = 5  # 最小请求间隔（秒）
```

### 自定义测试

```python
# 创建测试器
tester = ASRTester()

# 测试单个音频文件
await tester.test_audio_file("path/to/audio.wav", "测试描述")

# 仅测试连接
await tester.test_connection_only()

# 查看汇总
tester.print_summary()

# 保存结果
tester.save_results("custom_results.json")
```

### 诊断模式

如果遇到连接问题，运行诊断工具：

```bash
python3 diagnose_xunfei.py
```

诊断内容包括：
- 网络连通性测试
- DNS 解析测试
- 端口可达性测试
- WebSocket 连接测试
- 鉴权参数验证

## 📊 测试结果

### 成功的测试

```json
{
  "file": "test_audio/real/sample1.wav",
  "description": "真实语音测试",
  "timestamp": "2026-03-03T11:00:00",
  "success": true,
  "text": "你好，这是一个测试",
  "duration": 1.23
}
```

### 失败的测试

```json
{
  "file": "test_audio/real/sample2.wav",
  "description": "真实语音测试",
  "timestamp": "2026-03-03T11:01:00",
  "success": false,
  "error": "ConnectionResetError: Connection reset by peer",
  "duration": 0
}
```

## 🐛 常见问题

### 1. 连接超时

**原因**: 频繁请求触发限制

**解决**: 
- 等待 30-60 分钟
- 增加测试间隔
- 减少测试频率

### 2. 音频格式错误

**原因**: 音频格式不符合要求

**解决**:
- 检查采样率（16kHz）
- 检查声道数（单声道）
- 检查采样位数（16 bit）

### 3. 识别结果为空

**原因**: 
- 静音音频（正常）
- 音频质量差
- 音量太小

**解决**:
- 使用真实语音测试
- 提高音量
- 检查音频质量

### 4. 鉴权失败

**原因**: API 密钥错误或过期

**解决**:
- 检查 `config/api_keys.json`
- 确认服务已开通
- 确认配额充足

## 📝 最佳实践

1. **首次测试**
   - 先运行 `generate_test_audio.py`
   - 再运行 `test_asr_audio.py`
   - 观察测试结果

2. **真实语音测试**
   - 录制清晰的语音
   - 确保音频格式正确
   - 放到 `test_audio/real/` 目录
   - 运行测试

3. **生产环境**
   - 使用长连接
   - 实现重连机制
   - 添加错误处理
   - 监控成功率

4. **调试问题**
   - 查看详细日志
   - 使用诊断工具
   - 检查网络配置
   - 验证音频格式

## 🔗 相关链接

- [讯飞语音听写 API 文档](https://www.xfyun.cn/doc/asr/voicedictation/API.html)
- [讯飞控制台](https://console.xfyun.cn/)
- [项目 README](../README.md)

## 📧 反馈

如有问题或建议，请提交 Issue 或联系开发团队。
