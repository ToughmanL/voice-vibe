# 更新日志

所有重要的变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 支持更多LLM服务商（OpenAI、Claude）
- 音频文件上传功能
- 移动端适配

## [1.0.0] - 2026-03-02

### 新增
- ✨ 核心架构设计
  - 抽象基类定义（ASR/TTS/LLM/匹配引擎）
  - 清晰的接口规范
  - 易于扩展的架构

- 🎤 科大讯飞ASR集成
  - WebSocket实时语音识别
  - 流式识别支持
  - 动态修正（wpgs）
  - 鉴权URL自动生成

- 🔊 科大讯飞TTS集成
  - WebSocket流式语音合成
  - 多种预设音色
  - 自定义语速/音调/音量

- 🤖 Kimi LLM集成
  - 同步和流式对话
  - 8K/32K/128K上下文支持
  - 系统提示支持
  - 对话历史管理

- 💕 匹配引擎
  - 多维度特征匹配
  - 兴趣向量编码
  - 余弦相似度计算
  - 匹配理由生成

- 🌐 Web Demo
  - FastAPI后端服务
  - WebSocket实时通信
  - 响应式Web界面
  - RESTful API接口

- 🧪 测试
  - 完整的单元测试覆盖
  - 异步测试支持
  - Mock外部依赖
  - 集成测试

- 📚 文档
  - 详细的README
  - 技术架构文档
  - API文档（/docs）
  - 贡献指南

### 技术细节
- Python 3.9+ 支持
- 异步IO（asyncio）
- WebSocket双向通信
- 依赖注入设计模式
- 配置文件管理

## [0.1.0] - 2026-03-01

### 新增
- 项目初始化
- 基础架构文档
- MVP Demo（模拟数据）

---

## 版本命名规则

- **主版本号**：不兼容的API变更
- **次版本号**：向后兼容的功能新增
- **修订号**：向后兼容的问题修正

[Unreleased]: https://github.com/yourusername/ai-match-platform/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/ai-match-platform/releases/tag/v1.0.0
[0.1.0]: https://github.com/yourusername/ai-match-platform/releases/tag/v0.1.0
