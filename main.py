"""
Agent-S 基础使用示例
这个文件展示了如何使用 Agent-S 来控制你的电脑
"""

import io
import os
import platform
from pathlib import Path
import pyautogui
from PIL import Image
from dotenv import load_dotenv

# 加载 .env 文件
# 优先从当前目录加载，如果不存在则使用系统环境变量
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载环境变量文件: {env_path}")
else:
    print("⚠️  未找到 .env 文件，使用系统环境变量")
    print(f"   提示：可以复制 .env.example 为 .env 并配置 API 密钥")


def setup_local_logging():
    import logging, os, datetime

    os.makedirs("logs", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        fh = logging.FileHandler(f"logs/main-{ts}.log", encoding="utf-8")
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


def setup_mlflow_logging():
    import mlflow

    # Enable autologging with all features
    mlflow.openai.autolog()

    # Configure MLflow tracking
    mlflow.set_tracking_uri("http://localhost:8080")  # Use local MLflow server
    mlflow.set_experiment("agent-s")


setup_local_logging()
setup_mlflow_logging()

from gui_agents.s3.agents.agent_s import AgentS3
from gui_agents.s3.agents.grounding import OSWorldACI


def get_screenshot_observation(screen_width, screen_height):
    """获取屏幕截图并转换为 Agent 需要的格式

    Args:
        screen_width: 屏幕宽度
        screen_height: 屏幕高度

    Returns:
        包含 screenshot、screen_width、screen_height 的观察字典
    """
    # 获取屏幕截图
    screenshot = pyautogui.screenshot()

    # 转换为字节流（Agent 需要的格式）
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    screenshot_bytes = buffered.getvalue()

    return {
        "screenshot": screenshot_bytes,
        "screen_width": screen_width,
        "screen_height": screen_height,
    }


def example_1_simple_task():
    """示例 1：执行简单的桌面任务（使用 OpenRouter）"""
    print("=" * 50)
    print("示例 1：简单的桌面任务（OpenRouter）")
    print("=" * 50)

    # 获取屏幕尺寸
    screen_width, screen_height = pyautogui.size()
    current_platform = platform.system().lower()

    print(f"\n📊 系统信息:")
    print(f"   - 操作系统: {current_platform}")
    print(f"   - 屏幕尺寸: {screen_width}x{screen_height}")

    # 配置主模型参数
    engine_params = {
        "engine_type": "open_router",
        "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
    }

    # 配置 Grounding 模型参数
    engine_params_for_grounding = {
        "engine_type": "open_router",
        "model": os.getenv("OPENROUTER_GROUNDING_MODEL", "bytedance/ui-tars-1.5-7b"),
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "grounding_width": 1920,
        "grounding_height": 1080,
    }

    print(f"\n🔧 模型配置 (使用 OpenRouter):")
    print(f"   - 主模型: {engine_params['model']}")
    print(f"   - 主模型 API: {engine_params['base_url']}")
    print(
        f"   - 主模型 API Key: {'✓ 已设置' if engine_params['api_key'] else '✗ 未设置'}"
    )
    print(f"   - Grounding 模型: {engine_params_for_grounding['model']}")
    print(f"   - Grounding API: {engine_params_for_grounding['base_url']}")
    print(
        f"   - Grounding API Key: {'✓ 已设置' if engine_params_for_grounding['api_key'] else '✗ 未设置'}"
    )

    print("\n🔨 初始化 Agent...")

    # 初始化 Grounding Agent
    print("   - 正在初始化 Grounding Agent...")
    grounding_agent = OSWorldACI(
        env=None,  # 不使用本地代码环境
        platform=current_platform,
        engine_params_for_generation=engine_params,
        engine_params_for_grounding=engine_params_for_grounding,
        width=screen_width,
        height=screen_height,
    )
    print("   ✓ Grounding Agent 初始化完成")

    # 初始化 Agent-S3
    print("   - 正在初始化 Agent-S3...")
    agent = AgentS3(
        worker_engine_params=engine_params,
        grounding_agent=grounding_agent,
        platform=current_platform,
        max_trajectory_length=8,  # 保留最近 8 轮图像历史
        enable_reflection=True,  # 启用反思功能
    )
    print("   ✓ Agent-S3 初始化完成")
    print(f"   - 最大轨迹长度: 8")
    print(f"   - 反思功能: 启用")

    # 执行任务
    instruction = "打开浏览器并访问 https://www.baidu.com"

    print(f"\n" + "=" * 50)
    print(f"📋 任务指令: {instruction}")
    print("=" * 50)

    print("\n📸 正在获取屏幕截图...")
    observation = get_screenshot_observation(screen_width, screen_height)
    screenshot_size = len(observation["screenshot"]) / 1024
    print(f"   ✓ 截图完成 (大小: {screenshot_size:.1f} KB)")

    print("\n🤖 正在调用 Agent 生成操作...")
    print("   - 调用主模型分析任务...")
    print("   - 调用 Grounding 模型定位元素...")

    try:
        info, actions = agent.predict(instruction, observation)

        print("\nAgent 响应成功!")
        print(f"\n规划的操作:")
        for i, action in enumerate(actions, 1):
            print(f"   {i}. {action[:100]}{'...' if len(action) > 100 else ''}")

        if info:
            print(f"\n额外信息:")
            for key, value in info.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   - {key}: {value[:100]}...")
                else:
                    print(f"   - {key}: {value}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print(f"\n🔍 错误详情:")
        print(f"   - 错误类型: {type(e).__name__}")
        print(f"   - 错误信息: {str(e)}")
        import traceback

        print(f"\n📜 完整堆栈:")
        traceback.print_exc()


def main():
    """主函数：运行所有示例"""
    print(
        """
    ╔══════════════════════════════════════════════════╗
    ║         Agent-S 基础使用示例                     ║
    ║    开源的计算机控制 AI Agent 框架                 ║
    ║        OpenRouter 模型配置                       ║
    ╚══════════════════════════════════════════════════╝
    """
    )

    example_1_simple_task()


if __name__ == "__main__":
    main()
