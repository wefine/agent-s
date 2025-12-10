"""
Agent-S2.5 DSPy 版本简单能力测试
使用 DSPy 框架实现的 GUI 智能体测试
"""

import io
import os
import sys
import platform
from pathlib import Path
import pyautogui
from PIL import Image
from dotenv import load_dotenv
import datetime
import time
import logging

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载 .env 文件
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载环境变量文件: {env_path}")
else:
    print("⚠️  未找到 .env 文件，使用系统环境变量")
    print(f"   提示：可以复制 .env-sample 为 .env 并配置 API 密钥")


def setup_local_logging():
    """设置本地日志"""
    os.makedirs("logs", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(f"logs/dspy_s25_test-{ts}.log", encoding="utf-8")
        sh = logging.StreamHandler()
        fh.setLevel(logging.DEBUG)
        sh.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        fh.setFormatter(fmt)
        sh.setFormatter(fmt)
        logger.addHandler(fh)
        logger.addHandler(sh)

    # 提高内部模块日志的可见性
    logging.getLogger("desktopenv.agent").setLevel(logging.DEBUG)


setup_local_logging()

# 导入 DSPy 版本的组件
import dspy
from dspy_s25.agents.agent_s import AgentS2_5_DSPy
from dspy_s25.agents.grounding import OSWorldACI

current_platform = platform.system().lower()
paused = False


def configure_dspy(engine_params):
    """配置 DSPy 语言模型"""
    try:
        # 使用 dspy.LM 配置语言模型
        if engine_params.get("base_url"):
            lm = dspy.LM(
                model=engine_params["model"],
                api_key=engine_params["api_key"],
                api_base=engine_params["base_url"],
            )
        else:
            lm = dspy.LM(
                model=engine_params["model"],
                api_key=engine_params["api_key"],
            )

        dspy.configure(lm=lm)
        print("✓ DSPy 语言模型配置成功")
        return True
    except Exception as e:
        print(f"⚠️  DSPy 配置警告: {e}")
        print("   将尝试使用默认配置继续...")
        return False


def scale_screen_dimensions(width: int, height: int, max_dim_size: int):
    """缩放屏幕尺寸以确保适合模型上下文限制"""
    scale_factor = min(max_dim_size / width, max_dim_size / height, 1)
    safe_width = int(width * scale_factor)
    safe_height = int(height * scale_factor)
    return safe_width, safe_height


def get_screenshot_observation(scaled_width, scaled_height):
    """
    获取屏幕截图并转换为 Agent 需要的格式

    Args:
        scaled_width: 缩放后的屏幕宽度
        scaled_height: 缩放后的屏幕高度

    Returns:
        包含 screenshot 的观察字典
    """
    # 获取屏幕截图
    screenshot = pyautogui.screenshot()
    # 缩放截图以适应模型限制
    screenshot = screenshot.resize((scaled_width, scaled_height), Image.LANCZOS)

    # 转换为字节流（Agent 需要的格式）
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    screenshot_bytes = buffered.getvalue()

    return {
        "screenshot": screenshot_bytes,
    }


def run_agent(agent, instruction: str, scaled_width: int, scaled_height: int):
    """
    运行 Agent 执行任务

    Args:
        agent: AgentS2_5_DSPy 实例
        instruction: 任务指令
        scaled_width: 缩放后的屏幕宽度
        scaled_height: 缩放后的屏幕高度
    """
    global paused
    obs = {}

    for step in range(15):
        # 检查暂停状态
        while paused:
            time.sleep(0.1)

        # 获取屏幕截图
        observation = get_screenshot_observation(scaled_width, scaled_height)
        obs["screenshot"] = observation["screenshot"]

        # 再次检查暂停状态
        while paused:
            time.sleep(0.1)

        print(f"\n🔄 Step {step + 1}/15: Getting next action from agent...")

        # 从 agent 获取下一步动作
        info, code = agent.predict(instruction=instruction, observation=obs)

        # 检查是否完成或失败
        if code and len(code) > 0:
            code_str = str(code[0]).lower()

            if "done" in code_str or "fail" in code_str:
                if platform.system() == "Darwin":
                    os.system(
                        f'osascript -e \'display dialog "Task Completed" with title "DSPy Agent-S2.5" buttons "OK" default button "OK"\''
                    )
                elif platform.system() == "Linux":
                    os.system(
                        f'zenity --info --title="DSPy Agent-S2.5" --text="Task Completed" --width=200 --height=100'
                    )
                break

            if "next" in code_str:
                continue

            if "wait" in code_str:
                print("⏳ Agent requested wait...")
                time.sleep(5)
                continue

        # 执行动作
        if code and len(code) > 0:
            time.sleep(1.0)
            print("EXECUTING CODE:", code[0])

            # 检查暂停状态
            while paused:
                time.sleep(0.1)

            # 执行代码
            try:
                exec(code[0])
            except Exception as e:
                print(f"执行失败: {e}")

            time.sleep(1.0)


def test_simple_task():
    """简单能力测试：执行预定义的桌面任务"""
    print("=" * 60)
    print("Agent-S2.5 DSPy 版本简单能力测试")
    print("=" * 60)

    # 获取屏幕尺寸
    screen_width, screen_height = pyautogui.size()

    print(f"\n📊 系统信息:")
    print(f"   - 操作系统: {current_platform}")
    print(f"   - 屏幕尺寸: {screen_width}x{screen_height}")

    # 缩放屏幕尺寸以适应模型限制
    scaled_width, scaled_height = scale_screen_dimensions(
        screen_width, screen_height, max_dim_size=2400
    )
    print(f"   - 缩放后尺寸: {scaled_width}x{scaled_height}")

    # 配置主模型参数（从环境变量读取）
    engine_params = {
        "engine_type": os.getenv("PROVIDER", "open_router"),
        "model": os.getenv("MODEL", "openai/gpt-4o-mini"),
        "base_url": os.getenv("MODEL_URL", ""),
        "api_key": os.getenv("MODEL_API_KEY", os.getenv("OPENROUTER_API_KEY", "")),
    }

    # 如果使用 open_router，设置默认 base_url
    if engine_params["engine_type"] == "open_router" and not engine_params["base_url"]:
        engine_params["base_url"] = "https://openrouter.ai/api/v1"

    # 配置 Grounding 模型参数
    engine_params_for_grounding = {
        "engine_type": os.getenv("GROUND_PROVIDER", "open_router"),
        "model": os.getenv("GROUND_MODEL", "bytedance/ui-tars-1.5-7b"),
        "base_url": os.getenv("GROUND_URL", "https://openrouter.ai/api/v1"),
        "api_key": os.getenv("GROUND_API_KEY", os.getenv("OPENROUTER_API_KEY", "")),
        "grounding_width": int(os.getenv("GROUNDING_WIDTH", "1920")),
        "grounding_height": int(os.getenv("GROUNDING_HEIGHT", "1080")),
    }

    print(f"\n🔧 模型配置:")
    print(f"   - 主模型 Provider: {engine_params['engine_type']}")
    print(f"   - 主模型: {engine_params['model']}")
    print(f"   - 主模型 API: {engine_params['base_url']}")
    print(
        f"   - 主模型 API Key: {'✓ 已设置' if engine_params['api_key'] else '✗ 未设置'}"
    )
    print(f"   - Grounding Provider: {engine_params_for_grounding['engine_type']}")
    print(f"   - Grounding 模型: {engine_params_for_grounding['model']}")
    print(f"   - Grounding API: {engine_params_for_grounding['base_url']}")
    print(
        f"   - Grounding API Key: {'✓ 已设置' if engine_params_for_grounding['api_key'] else '✗ 未设置'}"
    )
    print(
        f"   - Grounding 尺寸: {engine_params_for_grounding['grounding_width']}x{engine_params_for_grounding['grounding_height']}"
    )

    print("\n🔨 配置 DSPy...")
    # 在初始化 Agent 前配置 DSPy
    configure_dspy(engine_params)

    print("\n🔨 初始化 Agent...")

    # 初始化 Grounding Agent
    print("   - 正在初始化 Grounding Agent (DSPy)...")
    grounding_agent = OSWorldACI(
        platform=current_platform,
        engine_params_for_generation=engine_params,
        engine_params_for_grounding=engine_params_for_grounding,
        width=screen_width,
        height=screen_height,
    )
    print("   ✓ Grounding Agent 初始化完成")

    # 初始化 Agent-S2.5 DSPy
    print("   - 正在初始化 Agent-S2.5 (DSPy 版本)...")
    max_trajectory_length = int(os.getenv("MAX_TRAJECTORY_LENGTH", "8"))
    enable_reflection = os.getenv("ENABLE_REFLECTION", "true").lower() == "true"

    agent = AgentS2_5_DSPy(
        engine_params,
        grounding_agent,
        platform=current_platform,
        max_trajectory_length=max_trajectory_length,
        enable_reflection=enable_reflection,
    )
    print("   ✓ Agent-S2.5 (DSPy) 初始化完成")
    print(f"   - 最大轨迹长度: {max_trajectory_length}")
    print(f"   - 反思功能: {'启用' if enable_reflection else '禁用'}")

    # 预定义测试任务（可以根据需要修改）
    instruction = os.getenv("TEST_TASK", "打开Google，查询深圳今天的天气")

    print(f"\n" + "=" * 60)
    print(f"📋 测试任务: {instruction}")
    print("=" * 60)

    try:
        # 重置 agent 状态
        agent.reset()

        # 运行 agent
        run_agent(agent, instruction, scaled_width, scaled_height)

        print("\n✅ 测试完成！")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print(f"\n🔍 错误详情:")
        print(f"   - 错误类型: {type(e).__name__}")
        print(f"   - 错误信息: {str(e)}")
        import traceback

        print(f"\n📜 完整堆栈:")
        traceback.print_exc()


import mlflow
import dspy

# Enable autologging with all features
mlflow.dspy.autolog(
    log_compiles=True,  # Track optimization process
    log_evals=True,  # Track evaluation results
    log_traces_from_compile=True,  # Track program traces during optimization
)
# Configure MLflow tracking
mlflow.set_tracking_uri("http://localhost:8080")  # Use local MLflow server
mlflow.set_experiment("dspy-s2")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 DSPy Agent-S2.5 测试程序")
    print("   使用 DSPy 框架实现的 GUI 智能体")
    print("=" * 60 + "\n")

    test_simple_task()


if __name__ == "__main__":
    main()
