# DSPy Agent-S2.5 实现

基于 DSPy 框架的 GUI 智能体实现，参考 Agent-S2.5 的设计思路。

## 🌟 特性

- **DSPy 框架**: 使用 DSPy 的 Signature 和 Module 构建结构化的智能体
- **模块化设计**: 清晰的模块划分（Agent、Worker、Grounding）
- **多模态支持**: 支持处理截图和文本输入
- **反思机制**: 可选的轨迹反思功能，检测循环和问题
- **扁平架构**: 无层级规划，减少推理时间

## 📁 目录结构

```
dspy_s25/
├── __init__.py              # 包初始化
├── README.md                # 本文档
├── test_simple.py           # 简单测试脚本
├── agents/                  # Agent 实现
│   ├── __init__.py
│   ├── agent_s.py          # 主 Agent 类
│   ├── worker.py           # Worker 模块
│   └── grounding.py        # Grounding 模块
├── core/                    # DSPy 核心模块
│   ├── __init__.py
│   ├── signatures.py       # DSPy Signatures
│   └── modules.py          # DSPy Modules
├── memory/                  # 记忆管理
│   ├── __init__.py
│   └── procedural_memory.py # 提示词记忆
└── utils/                   # 工具函数
    ├── __init__.py
    └── common_utils.py     # 通用工具
```

## 🚀 快速开始

### 1. 环境配置

确保已安装依赖（项目根目录的 pyproject.toml 已包含 `dspy>=3.0.4`）：

```bash
# 在项目根目录
pip install -e .
```

### 2. 配置环境变量

复制 `.env-sample` 为 `.env` 并配置 API 密钥：

```bash
cp .env-sample .env
```

编辑 `.env` 文件：

```env
# 主模型配置
PROVIDER=open_router
MODEL=openai/gpt-4o-mini
MODEL_API_KEY=your_api_key_here

# Grounding 模型配置
GROUND_PROVIDER=open_router
GROUND_URL=https://openrouter.ai/api/v1
GROUND_API_KEY=your_api_key_here
GROUND_MODEL=bytedance/ui-tars-1.5-7b
GROUNDING_WIDTH=1920
GROUNDING_HEIGHT=1080

# 测试任务（可选）
TEST_TASK=打开计算器

# Agent 配置（可选）
MAX_TRAJECTORY_LENGTH=8
ENABLE_REFLECTION=true
```

### 3. 运行测试

```bash
# 在项目根目录运行
python dspy_s25/test_simple.py
```

## 💡 使用示例

### 基础使用

```python
import os
from dspy_s25.agents.agent_s import AgentS2_5_DSPy
from dspy_s25.agents.grounding import OSWorldACI

# 配置引擎参数
engine_params = {
    "engine_type": "open_router",
    "model": "openai/gpt-4o-mini",
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
}

# 配置 Grounding 参数
grounding_params = {
    "engine_type": "open_router",
    "model": "bytedance/ui-tars-1.5-7b",
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "grounding_width": 1920,
    "grounding_height": 1080,
}

# 初始化 Grounding Agent
grounding_agent = OSWorldACI(
    platform="linux",
    engine_params_for_generation=engine_params,
    engine_params_for_grounding=grounding_params,
    width=1920,
    height=1080,
)

# 初始化 Agent
agent = AgentS2_5_DSPy(
    engine_params=engine_params,
    grounding_agent=grounding_agent,
    platform="linux",
    max_trajectory_length=8,
    enable_reflection=True,
)

# 执行任务
instruction = "打开浏览器并访问百度"
observation = {
    "screenshot": screenshot_bytes,  # 截图字节数据
}

info, actions = agent.predict(instruction, observation)

# 执行动作
for action in actions:
    exec(action)
```

### 自定义 DSPy 模块

```python
import dspy
from dspy_s25.core.signatures import ActionGenerationSignature

# 使用自定义配置
class CustomActionGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        # 使用 ChainOfThought 进行推理
        self.generate = dspy.ChainOfThought(ActionGenerationSignature)
    
    def forward(self, task_description, screenshot_analysis, **kwargs):
        return self.generate(
            task_description=task_description,
            screenshot_analysis=screenshot_analysis,
            **kwargs
        )
```

## 🏗️ 架构设计

### 核心组件

1. **AgentS2_5_DSPy** (agents/agent_s.py)
   - 主 Agent 类
   - 管理整体工作流程
   - 协调 Worker 和 Grounding Agent

2. **DSpyWorker** (agents/worker.py)
   - 基于 DSPy 的 Worker 模块
   - 生成具体的 GUI 操作动作
   - 管理动作历史和反思

3. **OSWorldACI** (agents/grounding.py)
   - Grounding Agent 实现
   - 将描述性动作转换为具体坐标
   - 执行实际的屏幕操作

4. **DSPy Modules** (core/modules.py)
   - ActionGenerator: 动作生成器
   - TrajectoryReflector: 轨迹反思器
   - GroundingModule: 坐标定位模块
   - MultiModalLMWrapper: 多模态 LM 包装器

5. **DSPy Signatures** (core/signatures.py)
   - ActionGenerationSignature: 动作生成签名
   - TrajectoryReflectionSignature: 轨迹反思签名
   - GroundingSignature: 坐标定位签名

### 工作流程

```
用户指令 → AgentS2_5_DSPy
    ↓
DSpyWorker
    ├── TrajectoryReflector (反思)
    ├── ActionGenerator (生成动作)
    └── 历史管理
    ↓
OSWorldACI (Grounding)
    ├── OCR 文本提取
    ├── 坐标定位
    └── 动作执行
    ↓
执行结果 → 下一轮
```

## 🎯 DSPy 特性应用

### 1. Signature 定义

使用 DSPy 的 Signature 清晰定义输入输出：

```python
class ActionGenerationSignature(dspy.Signature):
    """生成下一步 GUI 操作动作的签名"""
    
    task_description = dspy.InputField(desc="任务描述")
    screenshot_analysis = dspy.InputField(desc="当前截图分析")
    # ... 更多字段
    
    grounded_action_code = dspy.OutputField(desc="具体动作代码")
```

### 2. Module 构建

使用 DSPy 的 Module 和 Predict/ChainOfThought：

```python
class ActionGenerator(dspy.Module):
    def __init__(self, use_cot=True):
        super().__init__()
        if use_cot:
            self.generate = dspy.ChainOfThought(ActionGenerationSignature)
        else:
            self.generate = dspy.Predict(ActionGenerationSignature)
```

### 3. 可优化性

DSPy 的优化器可以自动优化提示词和参数：

```python
# 未来可以使用 DSPy 的优化器
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(metric=success_metric)
optimized_agent = optimizer.compile(agent, trainset=examples)
```

## 🔧 配置选项

### Engine Parameters

```python
engine_params = {
    "engine_type": "open_router",  # openai, anthropic, open_router
    "model": "openai/gpt-4o-mini",
    "base_url": "https://openrouter.ai/api/v1",  # 可选
    "api_key": "your_api_key",
    "temperature": 0.0,  # 可选
}
```

### Agent Parameters

```python
agent = AgentS2_5_DSPy(
    engine_params=engine_params,
    grounding_agent=grounding_agent,
    platform="linux",              # linux, darwin, windows
    max_trajectory_length=8,       # 最大历史图像数量
    enable_reflection=True,        # 是否启用反思
)
```

## 📝 与 s2_5 的对比

| 特性 | s2_5 原版 | dspy_s25 |
|-----|----------|----------|
| 框架 | 自定义 LMM 包装 | DSPy |
| 签名定义 | 隐式在提示词中 | 显式 Signature |
| 模块化 | 类继承 | DSPy Module |
| 可优化性 | 手动调整 | DSPy 优化器 |
| 提示词管理 | 字符串模板 | Signature + 模板 |
| 多模态 | 自定义实现 | DSPy + 自定义 |

## 🐛 调试

启用详细日志：

```python
import logging
logging.getLogger("desktopenv.agent").setLevel(logging.DEBUG)
```

查看日志文件：

```bash
tail -f logs/dspy_s25_test-*.log
```

## 📚 参考资料

- [DSPy 官方文档](https://github.com/stanfordnlp/dspy)
- [Agent-S 项目](https://github.com/simular-ai/Agent-S)
- [DSPy Paper](https://arxiv.org/abs/2310.03714)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

遵循项目主许可证。
