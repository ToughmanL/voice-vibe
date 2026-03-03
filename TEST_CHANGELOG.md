# 测试工具更新日志

## 2026-03-03 - 测试工具套件 v1.0

### ✨ 新增功能

#### 1. 测试音频生成器 (`generate_test_audio.py`)
- 自动生成多种测试音频
- 支持静音音频（1秒、3秒）
- 支持单音音频（440Hz、880Hz）
- 自动创建测试音频目录

#### 2. 完整测试工具 (`test_asr_audio.py`)
- 支持本地音频文件测试
- 内置频率限制保护
- 详细的测试报告
- JSON 格式结果输出
- 支持批量测试
- 自动音频格式验证

#### 3. 快速测试工具 (`quick_test.py`)
- 快速验证连接状态
- 2步测试（连接 + 识别）
- 清晰的测试结果
- 问题诊断建议

#### 4. 诊断工具 (`diagnose_xunfei.py`)
- 网络连通性测试
- DNS 解析测试
- 端口可达性测试
- WebSocket 连接测试
- 鉴权参数详细输出

#### 5. 文档
- `TEST_README.md` - 完整的使用指南
- 包含最佳实践和故障排除

### 🔧 修复问题

#### ASR 客户端修复
- ✅ 修复 WebSocket 参数错误（`timeout` → `open_timeout`）
- ✅ 更换推荐主机（`ws-api.xfyun.cn` → `iat-api.xfyun.cn`）
- ✅ 添加合理的超时设置

#### 频率限制处理
- ✅ 内置最小请求间隔控制
- ✅ 默认 5 秒间隔，可调整
- ✅ 测试间自动等待

### 📊 测试覆盖

#### 音频类型
- ✅ 静音音频测试
- ⚪ 单音音频测试（可选）
- ⚪ 真实语音测试（需用户提供）

#### 测试场景
- ✅ WebSocket 连接测试
- ✅ 音频上传测试
- ✅ 识别结果测试
- ✅ 错误处理测试

### 🎯 使用场景

#### 开发阶段
```bash
# 1. 生成测试音频
python3 generate_test_audio.py

# 2. 快速验证
python3 quick_test.py

# 3. 完整测试
python3 test_asr_audio.py
```

#### 调试阶段
```bash
# 诊断问题
python3 diagnose_xunfei.py
```

#### 生产环境
- 使用 `test_asr_audio.py` 作为集成测试
- 监控 `test_results.json` 中的成功率
- 定期运行快速测试验证服务可用性

### ⚠️ 注意事项

#### 频率限制
- 最小请求间隔: 5 秒
- 推荐测试间隔: 10 秒
- 频繁测试可能触发限制（需等待 30-60 分钟）

#### 音频格式
- 格式: WAV
- 采样率: 16kHz 或 8kHz
- 采样位数: 16 bit
- 声道: 单声道
- 编码: PCM

#### 真实语音测试
- 需要用户自行录制
- 推荐格式: 16kHz, 16bit, 单声道
- 保存路径: `test_audio/real/`

### 📝 下一步计划

- [ ] 添加音频录制功能
- [ ] 支持更多音频格式（MP3, FLAC）
- [ ] 添加性能基准测试
- [ ] 集成到 CI/CD 流程
- [ ] 添加 TTS 测试工具
- [ ] 添加完整的端到端测试（ASR + LLM + TTS）

---

## 使用示例

### 基础测试流程

```bash
# 1. 生成测试音频
$ python3 generate_test_audio.py
✅ 已生成: test_audio/silence_1s.wav
✅ 已生成: test_audio/silence_3s.wav
...

# 2. 快速测试
$ python3 quick_test.py
✅ 配置加载成功
✅ 连接成功！
✅ 识别完成
   结果: '' (静音音频应为空)

# 3. 完整测试
$ python3 test_asr_audio.py
[详细测试输出...]
测试结果已保存到: test_results.json
```

### 添加真实语音测试

```bash
# 1. 录制语音（使用 Audacity 或其他工具）
# 格式: 16kHz, 16bit, 单声道

# 2. 保存到测试目录
$ mkdir -p test_audio/real
$ cp my_voice.wav test_audio/real/

# 3. 运行测试
$ python3 test_asr_audio.py
```

---

**提示**: 测试工具已针对讯飞 API 的频率限制进行了优化，但仍建议避免过于频繁的测试。
