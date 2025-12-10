# DSPy Agent-S2.5 快速参考

## 📦 导入

```python
from dspy_s25 import (
    AgentS2_5_DSPy,      # 主Agent类
    OSWorldACI,          # Grounding模块
    DSpyWorker,          # Worker模块
    ActionGenerator,     # 动作生成器
    TrajectoryReflector, # 轨迹反思器
)
```

## 🚀 基本使用

```python
# 1. 配置引擎参数
engine_params = {
    "engine_type": "open_router",
    "model": "openai/gpt-4o-mini",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "base_url": "https://openrouter.ai/api/v1",
}

# 2. 初始化Grounding Agent
grounding_agent = OSWorldACI(
    platform="linux",  # "darwin", "windows"
    width=1920,
    height=1080,
)

# 3. 初始化Agent
agent = AgentS2_5_DSPy(
    engine_params=engine_params,
    grounding_agent=grounding_agent,
    max_trajectory_length=8,
    enable_reflection=True,
)

# 4. 重置状态（开始新任务）
agent.reset()

# 5. 执行预测
info, actions = agent.predict(
    instruction="打开计算器",
    observation={"screenshot": screenshot_bytes}
)

# 6. 执行动作
for action in actions:
    exec(action)
```

## 🎯 Agent配置参数

```python
AgentS2_5_DSPy(
    engine_params,          # 必需：LLM配置
    grounding_agent,        # 必需：Grounding Agent
    platform="linux",       # 可选：操作系统
    max_trajectory_length=8,  # 可选：历史长度
    enable_reflection=True,   # 可选：启用反思
)
```

## 🔧 引擎配置

### OpenRouter
```python
engine_params = {
    "engine_type": "open_router",
    "model": "openai/gpt-4o-mini",
    "api_key": "sk-or-...",
    "base_url": "https://openrouter.ai/api/v1",
}
```

### OpenAI
```python
engine_params = {
    "engine_type": "openai",
    "model": "gpt-4o-mini",
    "api_key": "sk-...",
}
```

### Anthropic
```python
engine_params = {
    "engine_type": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "api_key": "sk-ant-...",
}
```

## 📸 获取截图

```python
import io
import pyautogui
from PIL import Image

def get_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.resize((1920, 1080), Image.LANCZOS)
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    return buffered.getvalue()

# 使用
screenshot_bytes = get_screenshot()
observation = {"screenshot": screenshot_bytes}
```

## 🤖 可用动作

Grounding Agent支持的动作：

```python
agent.click(description, clicks=1, button="left")
agent.double_click(description)
agent.right_click(description)
agent.type(text)
agent.hotkey(*keys)
agent.scroll(description, clicks=-3)
agent.drag(start_desc, end_desc)
agent.wait(seconds)
agent.done()
agent.fail()
```

## 🔄 完整工作流程

```python
# 初始化
agent = AgentS2_5_DSPy(engine_params, grounding_agent)

# 任务循环
instruction = "打开浏览器并访问百度"
agent.reset()

for step in range(15):  # 最多15步
    # 获取截图
    screenshot = get_screenshot()
    observation = {"screenshot": screenshot}
    
    # 预测下一步
    info, actions = agent.predict(instruction, observation)
    
    # 检查完成
    if actions and ("done" in str(actions[0]).lower() or 
                   "fail" in str(actions[0]).lower()):
        break
    
    # 执行动作
    for action in actions:
        exec(action)
    
    # 等待
    time.sleep(1)
```

## 📊 返回信息

`predict()` 方法返回：

```python
info, actions = agent.predict(instruction, observation)

# info 字典包含:
info = {
    "full_plan": str,              # 完整计划
    "executor_plan": str,          # 执行计划
    "plan_code": str,              # 计划代码
    "reflection": str,             # 反思（如果启用）
    "previous_verification": str,  # 上一步验证
    "current_analysis": str,       # 当前状态分析
    "next_action_desc": str,       # 下一步动作描述
}

# actions 列表:
actions = ["agent.click(...)"]  # 可执行的动作
```

## 🐛 调试

```python
# 启用详细日志
import logging
logging.getLogger("desktopenv.agent").setLevel(logging.DEBUG)

# 查看日志文件
# logs/dspy_s25_test-YYYYMMDD@HHMMSS.log
```

## 🔑 环境变量

在 `.env` 文件中配置：

```env
# OpenRouter（推荐）
OPENROUTER_API_KEY=sk-or-v1-xxx

# 模型选择（可选）
PROVIDER=open_router
MODEL=openai/gpt-4o-mini
GROUND_MODEL=bytedance/ui-tars-1.5-7b

# Agent配置（可选）
MAX_TRAJECTORY_LENGTH=8
ENABLE_REFLECTION=true

# 测试任务（可选）
TEST_TASK=打开计算器
```

## 📝 常用任务示例

```python
# 打开应用
"打开计算器"
"打开记事本"
"打开文件管理器"

# 文本操作
"打开记事本并输入 Hello World"
"复制当前选中的文本"

# 浏览器操作
"打开浏览器并访问百度"
"在浏览器中搜索 Python"

# 文件操作
"打开文件管理器并进入 Documents"
"创建名为 test.txt 的文件"
```

## 🧩 DSPy Module使用

```python
from dspy_s25 import ActionGenerator, TrajectoryReflector

# 单独使用动作生成器
action_gen = ActionGenerator(use_cot=True)
result = action_gen(
    task_description="打开计算器",
    screenshot_analysis="桌面显示...",
    action_history="无历史",
    reflection="",
    text_buffer="[]",
)

# 单独使用反思器
reflector = TrajectoryReflector(use_cot=True)
result = reflector(
    task_description="打开计算器",
    current_trajectory="Step 1: ...",
    last_action="clicked menu",
)
```

## 📚 文档链接

- [完整文档](README.md)
- [快速入门](QUICKSTART.md)
- [安装指南](INSTALLATION.md)
- [对比分析](COMPARISON.md)
- [项目总结](PROJECT_SUMMARY.md)

## ⚡ 快速命令

```bash
# 安装
pip install -e .

# 测试
python dspy_s25/test_simple.py

# 示例
python dspy_s25/examples_usage.py

# 自定义任务
TEST_TASK="你的任务" python dspy_s25/test_simple.py
```

## 🆘 获取帮助

- 查看日志：`logs/dspy_s25_test-*.log`
- 提交Issue
- 阅读文档
- 查看示例代码

---

**快速参考 v1.0** | [返回主文档](README.md)
