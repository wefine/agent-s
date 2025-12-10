"""
验证 DSPy 配置是否正常
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ 已加载环境变量: {env_path}")
else:
    print("⚠️  未找到 .env 文件")

print("\n" + "=" * 60)
print("DSPy 配置验证")
print("=" * 60)

# 1. 检查 DSPy 安装
print("\n1️⃣ 检查 DSPy 安装...")
try:
    import dspy

    print(f"   ✓ DSPy 已安装")
    print(f"   版本: {dspy.__version__}")
except ImportError as e:
    print(f"   ✗ DSPy 未安装: {e}")
    print("   请运行: pip install dspy>=3.0.4")
    sys.exit(1)

# 2. 检查 API Key
print("\n2️⃣ 检查 API Key...")
api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("MODEL_API_KEY")
if api_key:
    print(f"   ✓ API Key 已设置")
    print(f"   前缀: {api_key[:10]}...")
else:
    print("   ✗ API Key 未设置")
    print("   请在 .env 文件中设置 OPENROUTER_API_KEY")
    sys.exit(1)

# 3. 测试 DSPy LM 初始化
print("\n3️⃣ 测试 DSPy LM 初始化...")
try:
    model = os.getenv("MODEL", "openai/gpt-4o-mini")
    base_url = os.getenv("MODEL_URL", "https://openrouter.ai/api/v1")

    print(f"   模型: {model}")
    print(f"   API: {base_url}")

    # 尝试初始化
    lm = dspy.LM(
        model=model,
        api_key=api_key,
        api_base=base_url,
    )
    print(f"   ✓ DSPy LM 初始化成功")

    # 配置 DSPy
    dspy.configure(lm=lm)
    print(f"   ✓ DSPy 配置成功")

    # 验证配置
    if hasattr(dspy.settings, "lm"):
        print(f"   ✓ DSPy settings.lm 已设置")

except AttributeError as e:
    print(f"   ⚠️  API 方法不存在: {e}")
    print("   这可能是 DSPy 版本问题")
    print("   提示: 请确保使用 DSPy >= 3.0.4")
    print("\n   替代方案：手动配置 DSPy")
    print("   请参考 DSPY_CONFIG.md 文档")
except Exception as e:
    print(f"   ✗ 初始化失败: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# 4. 测试 DSPy Module
print("\n4️⃣ 测试 DSPy Module...")
try:
    # 尝试创建一个简单的 Signature
    class TestSignature(dspy.Signature):
        """测试签名"""

        input_text = dspy.InputField(desc="输入文本")
        output_text = dspy.OutputField(desc="输出文本")

    print(f"   ✓ DSPy Signature 创建成功")

    # 尝试创建一个简单的 Module
    class TestModule(dspy.Module):
        def __init__(self):
            super().__init__()
            self.predictor = dspy.Predict(TestSignature)

        def forward(self, input_text):
            return self.predictor(input_text=input_text)

    module = TestModule()
    print(f"   ✓ DSPy Module 创建成功")

except Exception as e:
    print(f"   ✗ Module 创建失败: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# 5. 检查项目导入
print("\n5️⃣ 检查项目导入...")
try:
    # 添加项目路径
    sys.path.insert(0, str(project_root))

    from dspy_s25 import AgentS2_5_DSPy, OSWorldACI

    print(f"   ✓ dspy_s25 模块导入成功")

except ImportError as e:
    print(f"   ⚠️  模块导入失败: {e}")
    print("   这可能是因为缺少依赖（如 pyautogui）")
    print("   在实际使用环境中应该正常")

# 完成
print("\n" + "=" * 60)
print("✅ DSPy 配置验证完成！")
print("=" * 60)
print("\n可以开始使用 dspy_s25 了！")
print("运行: python dspy_s25/test_simple.py")
print("\n如有问题，请参考:")
print("  - DSPY_CONFIG.md - DSPy 配置详解")
print("  - QUICKSTART.md - 快速入门指南")
print("  - INSTALLATION.md - 安装指南")
