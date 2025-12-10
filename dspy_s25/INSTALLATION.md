# DSPy Agent-S2.5 安装指南

## 📋 系统要求

- **Python**: >= 3.13
- **操作系统**: Linux / macOS / Windows
- **依赖**: 已在 `pyproject.toml` 中定义

## 🔧 安装步骤

### 方法一：通过项目根目录安装（推荐）

```bash
# 1. 进入项目根目录
cd /home/0668000228/Gits/cua/agent-s

# 2. 安装项目（包含所有依赖）
pip install -e .
```

这会自动安装所有依赖，包括：
- ✅ dspy >= 3.0.4
- ✅ pyautogui >= 0.9.54
- ✅ pytesseract >= 0.3.13
- ✅ anthropic, openai, google-genai
- ✅ 其他必要依赖

### 方法二：手动安装依赖

如果你只想使用 dspy_s25 模块：

```bash
# 核心依赖
pip install dspy>=3.0.4
pip install pyautogui>=0.9.54
pip install pytesseract>=0.3.13
pip install pillow>=10.0.0

# LLM 支持
pip install openai>=2.6.1
pip install anthropic>=0.72.0
pip install google-genai>=1.46.0

# 其他工具
pip install python-dotenv>=1.2.1
```

## 🔍 验证安装

### 检查 DSPy

```bash
python -c "import dspy; print(f'DSPy 版本: {dspy.__version__}')"
```

预期输出：
```
DSPy 版本: 3.0.x
```

⚠️ **重要**: DSPy 3.x 使用了新的 API。请阅读 [DSPY_CONFIG.md](DSPY_CONFIG.md) 了解配置方法。

### 检查项目导入（需要完整依赖）

```bash
cd /home/0668000228/Gits/cua/agent-s
python -c "from dspy_s25 import AgentS2_5_DSPy; print('✓ 导入成功')"
```

### 检查 pyautogui（GUI 自动化必需）

```bash
python -c "import pyautogui; print(f'pyautogui 版本: {pyautogui.__version__}')"
```

## 🔑 配置 API 密钥

### 1. 创建 .env 文件

```bash
cd /home/0668000228/Gits/cua/agent-s
cp .env-sample .env
```

### 2. 编辑 .env 文件

```bash
nano .env  # 或使用你喜欢的编辑器
```

### 3. 填写必要的 API 密钥

最小配置（使用 OpenRouter）：
```env
# OpenRouter API Key（推荐，支持多种模型）
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选：自定义模型
MODEL=openai/gpt-4o-mini
GROUND_MODEL=bytedance/ui-tars-1.5-7b
```

或使用其他服务：

#### OpenAI
```env
PROVIDER=openai
MODEL=gpt-4o-mini
MODEL_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Anthropic
```env
PROVIDER=anthropic
MODEL=claude-3-5-sonnet-20241022
MODEL_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🧪 测试安装

### 运行简单测试

```bash
cd /home/0668000228/Gits/cua/agent-s
python dspy_s25/test_simple.py
```

如果一切正常，你应该看到：
```
✅ 已加载环境变量文件: /path/to/.env
📊 系统信息:
   - 操作系统: linux
   - 屏幕尺寸: 1920x1080
   ...
```

### 运行使用示例

```bash
python dspy_s25/examples_usage.py
```

## 🐛 常见问题

### 问题1: ModuleNotFoundError: No module named 'dspy'

**解决方案**:
```bash
pip install dspy>=3.0.4
```

### 问题2: ModuleNotFoundError: No module named 'pyautogui'

**解决方案**:
```bash
pip install pyautogui>=0.9.54
```

在 Linux 上可能还需要：
```bash
sudo apt-get install python3-tk python3-dev
```

在 macOS 上可能还需要：
```bash
# 授予终端辅助功能权限
# 系统偏好设置 -> 安全性与隐私 -> 辅助功能
```

### 问题3: ImportError: cannot import name 'AgentS2_5_DSPy'

**解决方案**:
确保在项目根目录运行：
```bash
cd /home/0668000228/Gits/cua/agent-s
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python dspy_s25/test_simple.py
```

或者安装项目：
```bash
pip install -e .
```

### 问题4: pytesseract.pytesseract.TesseractNotFoundError

**解决方案**:
安装 Tesseract OCR：

**Linux**:
```bash
sudo apt-get install tesseract-ocr
```

**macOS**:
```bash
brew install tesseract
```

**Windows**:
下载并安装: https://github.com/UB-Mannheim/tesseract/wiki

### 问题5: No API Key 错误

**解决方案**:
1. 确保 `.env` 文件存在
2. 确保 API Key 正确填写
3. 检查环境变量是否加载：
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENROUTER_API_KEY'))"
```

## 📦 依赖清单

### 核心依赖
- dspy >= 3.0.4
- pyautogui >= 0.9.54
- pytesseract >= 0.3.13
- pillow >= 10.0.0
- python-dotenv >= 1.2.1

### LLM 支持
- openai >= 2.6.1
- anthropic >= 0.72.0
- google-genai >= 1.46.0

### 可选依赖
- mlflow >= 3.5.1 (用于日志追踪)
- pandas >= 2.3.3 (数据处理)

## 🚀 开始使用

安装完成后，参考：
- `QUICKSTART.md` - 5分钟快速入门
- `README.md` - 完整文档
- `examples_usage.py` - 使用示例

## 💡 提示

1. **首次使用**: 建议先运行 `test_simple.py` 确保一切正常
2. **API Key**: 使用 OpenRouter 可以访问多种模型
3. **权限**: 在 macOS 上需要授予辅助功能权限
4. **网络**: 确保可以访问 API 服务（可能需要代理）

## 📞 获取帮助

如果遇到问题：
1. 查看本文档的常见问题部分
2. 检查 `logs/` 目录下的日志文件
3. 提交 Issue 并附上错误信息

---

**祝你使用愉快！** 🎉
