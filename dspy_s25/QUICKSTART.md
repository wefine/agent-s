# DSPy Agent-S2.5 快速入门

5分钟快速上手 DSPy 版本的 Agent-S2.5！

## 🚀 快速开始

### 第一步：检查依赖

```bash
# 在项目根目录
cd /home/0668000228/Gits/cua/agent-s

# 确认 dspy 已安装
python -c "import dspy; print(f'DSPy version: {dspy.__version__}')"
```

如果未安装，运行：
```bash
pip install -e .
```

### 第二步：配置 API 密钥

编辑 `.env` 文件（如果没有，从 `.env-sample` 复制）：

```bash
cp .env-sample .env
nano .env  # 或使用你喜欢的编辑器
```

最小配置（使用 OpenRouter）：
```env
# OpenRouter API Key（必需）
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# 主模型（可选，默认 gpt-4o-mini）
MODEL=openai/gpt-4o-mini

# Grounding 模型（可选，默认 ui-tars）
GROUND_MODEL=bytedance/ui-tars-1.5-7b
```

### 第三步：运行测试

```bash
# 在项目根目录
python dspy_s25/test_simple.py
```

默认会执行任务："打开计算器"

自定义任务：
```bash
TEST_TASK="打开浏览器" python dspy_s25/test_simple.py
```

## 📖 5分钟教程

### 1. 基础使用

创建文件 `my_first_agent.py`:

```python
import os
import dspy
from dspy_s25 import AgentS2_5_DSPy, OSWorldACI
from dotenv import load_dotenv

load_dotenv()

# ⚠️ 重要：首先配置 DSPy
lm = dspy.LM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    api_base="https://openrouter.ai/api/v1",
)
dspy.configure(lm=lm)
print("✓ DSPy 已配置")

# 配置引擎参数
engine_params = {
    "engine_type": "open_router",
    "model": "openai/gpt-4o-mini",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "base_url": "https://openrouter.ai/api/v1",
}

# 初始化 Grounding Agent
grounding_agent = OSWorldACI(
    platform="linux",  # 或 "darwin" (macOS), "windows"
    width=1920,
    height=1080,
)

# 初始化 Agent
agent = AgentS2_5_DSPy(
    engine_params=engine_params,
    grounding_agent=grounding_agent,
)

# 使用 agent
instruction = "打开文件管理器"
observation = {
    "screenshot": screenshot_bytes,  # 从 pyautogui.screenshot() 获取
}

info, actions = agent.predict(instruction, observation)
print(f"计划: {info['executor_plan']}")
```

### 2. 完整示例（带截图）

```python
import io
import pyautogui
from PIL import Image

def get_screenshot():
    """获取当前屏幕截图"""
    screenshot = pyautogui.screenshot()
    # 可选：调整大小
    screenshot = screenshot.resize((1920, 1080), Image.LANCZOS)
    # 转换为字节
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    return buffered.getvalue()

# 获取截图
screenshot_bytes = get_screenshot()

# 执行任务
observation = {"screenshot": screenshot_bytes}
info, actions = agent.predict("打开记事本", observation)

# 执行动作
for action in actions:
    exec(action)
```

### 3. 多步骤任务

```python
# 重置 agent
agent.reset()

instruction = "打开浏览器并访问百度"

for step in range(10):  # 最多10步
    # 获取当前截图
    screenshot = get_screenshot()
    observation = {"screenshot": screenshot}
    
    # 获取下一步动作
    info, actions = agent.predict(instruction, observation)
    
    # 检查是否完成
    if actions and "done" in str(actions[0]).lower():
        print("✓ 任务完成！")
        break
    
    # 执行动作
    for action in actions:
        exec(action)
    
    # 等待一下
    import time
    time.sleep(1)
```

## 🎯 常见任务示例

### 打开应用程序

```python
tasks = [
    "打开计算器",
    "打开记事本",
    "打开文件管理器",
    "打开浏览器",
]

for task in tasks:
    agent.reset()
    # ... 执行任务
```

### 文本操作

```python
instructions = [
    "打开记事本并输入 Hello World",
    "在浏览器中搜索 Python DSPy",
    "复制当前选中的文本",
]
```

### 文件操作

```python
instructions = [
    "打开文件管理器并进入 Documents 文件夹",
    "创建一个名为 test.txt 的文件",
    "删除桌面上的 temp 文件夹",
]
```

## 🔧 配置选项

### Agent 配置

```python
agent = AgentS2_5_DSPy(
    engine_params=engine_params,
    grounding_agent=grounding_agent,
    platform="linux",              # 操作系统
    max_trajectory_length=8,       # 历史长度
    enable_reflection=True,        # 启用反思
)
```

### 引擎配置

```python
# OpenAI
engine_params = {
    "engine_type": "openai",
    "model": "gpt-4o-mini",
    "api_key": "sk-...",
}

# Anthropic
engine_params = {
    "engine_type": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "api_key": "sk-ant-...",
}

# OpenRouter
engine_params = {
    "engine_type": "open_router",
    "model": "openai/gpt-4o-mini",
    "api_key": "sk-or-...",
    "base_url": "https://openrouter.ai/api/v1",
}
```

## 📚 下一步

- 📖 阅读 [完整文档](README.md)
- 🆚 查看 [与原版对比](COMPARISON.md)
- 💡 浏览 [使用示例](examples_usage.py)
- 🔬 学习 [DSPy 框架](https://github.com/stanfordnlp/dspy)

## 🐛 常见问题

### Q: AttributeError: module 'dspy' has no attribute 'OpenAI'

A: DSPy 3.x 不再使用 `dspy.OpenAI()`。请使用：

```python
import dspy

lm = dspy.LM(
    model="openai/gpt-4o-mini",
    api_key="your-key",
    api_base="https://openrouter.ai/api/v1"
)
dspy.configure(lm=lm)
```

详见 [DSPY_CONFIG.md](DSPY_CONFIG.md)

### Q: 没有 API Key 怎么办？

A: 你需要从以下平台之一获取 API Key：
- [OpenRouter](https://openrouter.ai/) - 支持多种模型
- [OpenAI](https://platform.openai.com/)
- [Anthropic](https://www.anthropic.com/)

### Q: 程序卡住了怎么办？

A: 检查：
1. API Key 是否正确
2. 网络连接是否正常
3. 查看日志文件 `logs/dspy_s25_test-*.log`

### Q: 如何调试？

A: 启用详细日志：

```python
import logging
logging.getLogger("desktopenv.agent").setLevel(logging.DEBUG)
```

### Q: 任务失败了怎么办？

A: 检查：
1. 任务描述是否清晰
2. 屏幕截图是否正确
3. Grounding 模型是否支持你的分辨率

### Q: 如何提高性能？

A: 尝试：
1. 使用更强大的模型（如 gpt-4）
2. 启用反思功能
3. 增加 max_trajectory_length
4. 优化提示词（使用 DSPy 优化器）

## 💬 获取帮助

- 📧 提交 Issue
- 💬 查看文档
- 🤝 加入讨论

## ✨ 快速参考

```python
# 导入
from dspy_s25 import AgentS2_5_DSPy, OSWorldACI

# 初始化
agent = AgentS2_5_DSPy(engine_params, grounding_agent)

# 重置
agent.reset()

# 预测
info, actions = agent.predict(instruction, observation)

# 执行
for action in actions:
    exec(action)
```

**就是这么简单！开始构建你的 GUI 智能体吧！** 🚀
