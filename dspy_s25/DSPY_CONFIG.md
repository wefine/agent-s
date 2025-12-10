# DSPy 配置说明

由于 DSPy 3.x 的 API 与之前版本有所不同，这里提供配置指南。

## DSPy 语言模型配置

### 方式一：使用 dspy.LM (DSPy 3.x 推荐)

```python
import dspy

# OpenAI
lm = dspy.LM(model="gpt-4o-mini", api_key="your-key")
dspy.configure(lm=lm)

# OpenRouter (OpenAI 兼容)
lm = dspy.LM(
    model="openai/gpt-4o-mini",
    api_key="your-openrouter-key",
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)

# Anthropic
lm = dspy.LM(model="anthropic/claude-3-5-sonnet-20241022", api_key="your-key")
dspy.configure(lm=lm)
```

### 方式二：直接配置（简化版）

如果遇到 API 问题，可以在使用前手动配置：

```python
import dspy
import os

# 在使用 Agent 之前配置
lm = dspy.LM(
    model=os.getenv("MODEL", "openai/gpt-4o-mini"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)

# 然后再初始化 Agent
from dspy_s25 import AgentS2_5_DSPy, OSWorldACI
# ...
```

## 跳过自动 LM 初始化

如果想完全控制 DSPy 配置，可以在创建 Agent 前手动配置，然后传入配置参数时只用于 Grounding：

```python
import dspy
import os

# 1. 手动配置 DSPy
lm = dspy.LM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)

# 2. 创建 Agent（MultiModalLMWrapper 会尝试初始化，但不影响已配置的 DSPy）
engine_params = {
    "engine_type": "open_router",
    "model": "openai/gpt-4o-mini",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "base_url": "https://openrouter.ai/api/v1",
}

grounding_agent = OSWorldACI(...)
agent = AgentS2_5_DSPy(engine_params, grounding_agent, ...)
```

## 常见问题

### Q: AttributeError: module 'dspy' has no attribute 'OpenAI'

A: DSPy 3.x 不再使用 `dspy.OpenAI()`，而是使用 `dspy.LM()`。代码已更新为使用新 API。

### Q: 如何验证 DSPy 配置？

A: 运行以下代码测试：

```python
import dspy

# 配置
lm = dspy.LM(model="openai/gpt-4o-mini", api_key="your-key")
dspy.configure(lm=lm)

# 测试
print("DSPy 配置成功！")
print(f"当前 LM: {dspy.settings.lm}")
```

### Q: 能否使用其他模型？

A: 可以！DSPy 支持多种模型：

```python
# Cohere
lm = dspy.LM(model="cohere/command-r-plus", api_key="...")

# Together AI
lm = dspy.LM(model="together_ai/meta-llama/Llama-3-70b-chat-hf", api_key="...")

# Groq
lm = dspy.LM(model="groq/llama-3.1-70b-versatile", api_key="...")
```

## 降级到旧版本

如果需要使用旧版 DSPy API，可以：

```bash
pip install dspy-ai==2.4.x  # 安装旧版本
```

然后使用旧 API：
```python
import dspy

lm = dspy.OpenAI(model="gpt-4o-mini", api_key="...")
dspy.settings.configure(lm=lm)
```

## 推荐配置

最简单的配置方式（使用 OpenRouter）：

```python
import dspy
import os
from dotenv import load_dotenv

load_dotenv()

# 一行配置
lm = dspy.LM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)

# 现在可以使用 Agent 了
from dspy_s25 import AgentS2_5_DSPy, OSWorldACI
# ...
```

## 更多信息

- [DSPy 官方文档](https://github.com/stanfordnlp/dspy)
- [DSPy 模型配置](https://dspy-docs.vercel.app/docs/building-blocks/language_models)
