"""
DSPy Agent-S2.5 使用示例
展示如何使用 DSPy 框架的各个组件
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def example_1_basic_usage():
    """示例 1: 基础使用 - 完整流程"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)

    from dspy_s25 import AgentS2_5_DSPy, OSWorldACI

    # 配置引擎参数
    engine_params = {
        "engine_type": "open_router",
        "model": "openai/gpt-4o-mini",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
    }

    grounding_params = {
        "engine_type": "open_router",
        "model": "bytedance/ui-tars-1.5-7b",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "grounding_width": 1920,
        "grounding_height": 1080,
    }

    # 初始化组件
    grounding_agent = OSWorldACI(
        platform="linux",
        engine_params_for_generation=engine_params,
        engine_params_for_grounding=grounding_params,
        width=1920,
        height=1080,
    )

    agent = AgentS2_5_DSPy(
        engine_params=engine_params,
        grounding_agent=grounding_agent,
        platform="linux",
        max_trajectory_length=8,
        enable_reflection=True,
    )

    print("✓ Agent 初始化完成")
    print(f"  - 反思功能: 启用")
    print(f"  - 最大轨迹长度: 8")


def example_2_dspy_modules():
    """示例 2: 直接使用 DSPy 模块"""
    print("\n" + "=" * 60)
    print("示例 2: 直接使用 DSPy 模块")
    print("=" * 60)

    import dspy
    from dspy_s25 import ActionGenerator, MultiModalLMWrapper

    # 配置语言模型
    lm_config = {
        "engine_type": "open_router",
        "model": "openai/gpt-4o-mini",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "base_url": "https://openrouter.ai/api/v1",
        "temperature": 0.0,
    }

    # 初始化 LM
    lm_wrapper = MultiModalLMWrapper(lm_config)
    print("✓ 语言模型初始化完成")

    # 创建动作生成器
    action_gen = ActionGenerator(use_cot=True)
    print("✓ ActionGenerator 创建完成")

    # 使用动作生成器（示例，不实际调用）
    print("\n可以这样使用:")
    print(
        """
    result = action_gen(
        task_description="打开计算器",
        screenshot_analysis="当前桌面显示...",
        action_history="无历史动作",
        reflection="",
        text_buffer="[]",
    )
    """
    )


def example_3_custom_signature():
    """示例 3: 自定义 DSPy Signature"""
    print("\n" + "=" * 60)
    print("示例 3: 自定义 DSPy Signature")
    print("=" * 60)

    import dspy

    # 定义自定义 Signature
    class CustomUIActionSignature(dspy.Signature):
        """自定义的 UI 动作签名"""

        task = dspy.InputField(desc="要完成的任务")
        current_state = dspy.InputField(desc="当前 UI 状态")

        action = dspy.OutputField(desc="要执行的动作")
        confidence = dspy.OutputField(desc="执行信心 (0-1)")

    print("✓ 自定义 Signature 定义完成")
    print("\n可以这样使用:")
    print(
        """
    class CustomAgent(dspy.Module):
        def __init__(self):
            super().__init__()
            self.predict = dspy.ChainOfThought(CustomUIActionSignature)
        
        def forward(self, task, current_state):
            return self.predict(task=task, current_state=current_state)
    """
    )


def example_4_grounding_agent():
    """示例 4: 使用 Grounding Agent"""
    print("\n" + "=" * 60)
    print("示例 4: 使用 Grounding Agent")
    print("=" * 60)

    from dspy_s25 import OSWorldACI

    # 创建 Grounding Agent
    grounding_agent = OSWorldACI(
        platform="linux",
        width=1920,
        height=1080,
    )

    print("✓ Grounding Agent 创建完成")
    print("\n可用的动作:")
    print("  - agent.click(description, clicks=1, button='left')")
    print("  - agent.double_click(description)")
    print("  - agent.right_click(description)")
    print("  - agent.type(text)")
    print("  - agent.hotkey(*keys)")
    print("  - agent.scroll(description, clicks=-3)")
    print("  - agent.drag(start_desc, end_desc)")
    print("  - agent.wait(seconds)")
    print("  - agent.done()")
    print("  - agent.fail()")


def example_5_worker_usage():
    """示例 5: 单独使用 Worker"""
    print("\n" + "=" * 60)
    print("示例 5: 单独使用 Worker")
    print("=" * 60)

    from dspy_s25 import DSpyWorker, OSWorldACI

    engine_params = {
        "engine_type": "open_router",
        "model": "openai/gpt-4o-mini",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "base_url": "https://openrouter.ai/api/v1",
    }

    grounding_agent = OSWorldACI(platform="linux")

    # 创建 Worker
    worker = DSpyWorker(
        engine_params=engine_params,
        grounding_agent=grounding_agent,
        platform="linux",
        max_trajectory_length=8,
        enable_reflection=True,
    )

    print("✓ Worker 创建完成")
    print("\n可以这样使用:")
    print(
        """
    # 生成下一步动作
    info, actions = worker.generate_next_action(
        instruction="打开文件管理器",
        obs={"screenshot": screenshot_bytes}
    )
    
    # 执行动作
    for action in actions:
        exec(action)
    """
    )


def example_6_reflection():
    """示例 6: 使用反思功能"""
    print("\n" + "=" * 60)
    print("示例 6: 使用反思功能")
    print("=" * 60)

    from dspy_s25 import TrajectoryReflector

    # 创建反思器
    reflector = TrajectoryReflector(use_cot=True)

    print("✓ TrajectoryReflector 创建完成")
    print("\n反思器的作用:")
    print("  - 检测动作循环")
    print("  - 分析轨迹是否正常")
    print("  - 提供改进建议")
    print("\n可以这样使用:")
    print(
        """
    result = reflector(
        task_description="打开浏览器",
        current_trajectory="Step 1: clicked menu...",
        last_action="clicked menu button",
    )
    
    reflection = result.reflection
    """
    )


def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print("🚀 DSPy Agent-S2.5 使用示例集")
    print("=" * 70 + "\n")

    examples = [
        example_1_basic_usage,
        example_2_dspy_modules,
        example_3_custom_signature,
        example_4_grounding_agent,
        example_5_worker_usage,
        example_6_reflection,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n⚠️  示例运行出错: {e}")

    print("\n" + "=" * 70)
    print("✅ 所有示例展示完成!")
    print("=" * 70 + "\n")
    print("提示: 这些示例展示了如何使用各个组件，")
    print("      实际使用时请确保配置了正确的 API 密钥。")


if __name__ == "__main__":
    main()
