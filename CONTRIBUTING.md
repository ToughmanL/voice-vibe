# 贡献指南

感谢你考虑为AI语音匹配平台做贡献！

## 🤔 如何贡献

### 报告Bug

如果你发现了Bug，请：
1. 检查 [Issues](https://github.com/yourusername/ai-match-platform/issues) 中是否已有人报告
2. 如果没有，创建新Issue，包含：
   - 清晰的标题
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息（Python版本、操作系统等）

### 提出新功能

1. 在Issues中描述你的想法
2. 说明使用场景和价值
3. 等待维护者反馈后再开始实现

### 提交代码

1. Fork仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 编写代码和测试
4. 确保测试通过：`pytest`
5. 提交代码：`git commit -m 'Add amazing feature'`
6. 推送分支：`git push origin feature/amazing-feature`
7. 创建Pull Request

## 📋 代码规范

### Python代码

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- 使用 `black` 格式化代码
- 使用类型注解
- 编写文档字符串（Google风格）

示例：
```python
async def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
    """
    对话补全
    
    Args:
        messages: 对话历史
        temperature: 温度参数
    
    Returns:
        模型回复
    
    Raises:
        Exception: API调用失败
    """
    pass
```

### 测试要求

- 所有新功能必须有单元测试
- 测试覆盖率不低于80%
- 使用 `pytest` 和 `pytest-asyncio`

### 提交信息

使用清晰的提交信息：

```
类型: 简短描述

详细说明（可选）

类型包括：
- feat: 新功能
- fix: Bug修复
- docs: 文档更新
- test: 测试相关
- refactor: 重构
- style: 代码格式
```

示例：
```
feat: 添加语音情感分析功能

实现基于语调和语速的情感分析，用于增强匹配算法
```

## 🧪 运行测试

```bash
# 所有测试
pytest

# 特定测试
pytest tests/test_matcher.py -v

# 覆盖率报告
pytest --cov=src --cov-report=html
```

## 📚 开发设置

```bash
# 克隆你的Fork
git clone https://github.com/yourusername/ai-match-platform.git
cd ai-match-platform

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有

# 安装pre-commit hooks（可选）
pre-commit install
```

## 🎯 开发重点

当前优先级：

**高优先级：**
- 性能优化（降低延迟）
- 错误处理和容错机制
- 测试覆盖率提升

**中优先级：**
- 更多LLM服务商支持（OpenAI、Claude等）
- 匹配算法优化
- Web UI改进

**低优先级：**
- 移动端适配
- 国际化
- 高级匹配特征

## ❓ 有问题？

- 提Issue：https://github.com/yourusername/ai-match-platform/issues
- 邮件：your.email@example.com

再次感谢你的贡献！🎉
