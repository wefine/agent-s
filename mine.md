# 项目文档

## uv 包管理器使用指南

### 从 requirements.txt 安装依赖

使用 `uv` 从 `requirements.txt` 文件安装依赖非常简单，主要有以下几种方式：

#### 基本安装命令

```bash
uv pip install -r requirements.txt
```

这是最常用的命令，会读取 `requirements.txt` 文件并安装其中列出的所有依赖项。

#### 其他相关命令

##### 1. 安装到虚拟环境
```bash
uv venv
uv pip install -r requirements.txt
```

##### 2. 从其他格式文件安装
```bash
# 从 pyproject.toml 安装
uv pip install -r pyproject.toml

# 从 requirements.in 安装
uv pip install -r requirements.in
```

##### 3. 同步安装（推荐用于生产环境）
```bash
uv pip sync requirements.txt
```

`uv pip sync` 命令会：
- 安装 `requirements.txt` 中的所有依赖
- 卸载不在文件中的包
- 确保环境与文件完全一致

#### 注意事项

1. **确保文件存在**：运行命令前请确保项目目录中存在 `requirements.txt` 文件
2. **虚拟环境**：建议在虚拟环境中安装依赖，可以使用 `uv venv` 创建
3. **权限问题**：如果遇到权限问题，可能需要使用 `--user` 参数

#### 示例工作流

```bash
# 1. 创建虚拟环境
uv venv

# 2. 激活虚拟环境（Windows）
.venv\Scripts\activate

# 3. 安装依赖
uv pip install -r requirements.txt
```

### 项目依赖说明

当前项目的 `requirements.txt` 包含以下依赖：

- **核心依赖**：numpy, pandas, scikit-learn
- **AI/ML 服务**：openai, anthropic, together, google-genai
- **Web 框架**：fastapi, uvicorn
- **OCR 相关**：paddleocr, paddlepaddle, pytesseract
- **工具库**：backoff, websockets, tiktoken, pyautogui, toml, black
- **平台特定依赖**：
  - macOS: pyobjc
  - Windows: pywinauto, pywin32

`uv` 是一个快速的 Python 包管理器，比传统的 `pip` 快很多，特别适合现代 Python 项目开发。
