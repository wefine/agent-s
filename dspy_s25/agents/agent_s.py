"""
Agent-S DSPy 实现
基于 DSPy 框架的 GUI 智能体主入口
"""

import logging
import platform
from typing import Dict, List, Tuple

from dspy_s25.agents.grounding import ACI
from dspy_s25.agents.worker import DSpyWorker

logger = logging.getLogger("desktopenv.agent")


class UIAgent:
    """UI 自动化智能体基类"""

    def __init__(
        self,
        engine_params: Dict,
        grounding_agent: ACI,
        platform: str = platform.system().lower(),
    ):
        """
        初始化 UI Agent

        Args:
            engine_params: 语言模型配置参数
            grounding_agent: Grounding Agent 实例
            platform: 操作系统平台 (linux, darwin, windows)
        """
        self.engine_params = engine_params
        self.grounding_agent = grounding_agent
        self.platform = platform

        logger.info(f"UIAgent 初始化: platform={platform}")

    def reset(self) -> None:
        """重置 Agent 状态"""
        pass

    def predict(self, instruction: str, observation: Dict) -> Tuple[Dict, List[str]]:
        """
        生成下一步动作预测

        Args:
            instruction: 自然语言指令
            observation: 当前 UI 状态观察

        Returns:
            (info_dict, actions_list) 元组
        """
        pass


class AgentS2_5_DSPy(UIAgent):
    """
    基于 DSPy 的 Agent-S2.5 实现
    扁平化架构，无层级规划，以减少推理时间
    """

    def __init__(
        self,
        engine_params: Dict,
        grounding_agent: ACI,
        platform: str = platform.system().lower(),
        max_trajectory_length: int = 8,
        enable_reflection: bool = True,
    ):
        """
        初始化 Agent-S2.5 DSPy 版本

        Args:
            engine_params: 语言模型配置参数
            grounding_agent: Grounding Agent 实例
            platform: 操作系统平台
            max_trajectory_length: 最大图像轨迹长度
            enable_reflection: 是否启用反思功能
        """
        super().__init__(engine_params, grounding_agent, platform)

        self.max_trajectory_length = max_trajectory_length
        self.enable_reflection = enable_reflection

        logger.info(
            f"AgentS2_5_DSPy 初始化: "
            f"trajectory_length={max_trajectory_length}, "
            f"reflection={'启用' if enable_reflection else '禁用'}"
        )

        # 初始化组件
        self.reset()

    def reset(self) -> None:
        """重置 Agent 状态并初始化组件"""
        self.executor = DSpyWorker(
            engine_params=self.engine_params,
            grounding_agent=self.grounding_agent,
            platform=self.platform,
            max_trajectory_length=self.max_trajectory_length,
            enable_reflection=self.enable_reflection,
        )

        logger.info("Agent 状态已重置")

    def predict(self, instruction: str, observation: Dict) -> Tuple[Dict, List[str]]:
        """
        预测并生成下一步动作

        Args:
            instruction: 任务指令 (自然语言)
            observation: 观察数据，包含:
                - screenshot: 截图字节数据
                - (可选) 其他环境信息

        Returns:
            (info, actions) 元组
            - info: 包含计划、反思等信息的字典
            - actions: 可执行的动作列表
        """
        try:
            # 使用 executor (Worker) 生成下一步动作
            executor_info, actions = self.executor.generate_next_action(
                instruction=instruction, obs=observation
            )

            # 合并所有信息
            info = {**executor_info}

            logger.info(f"预测完成: {len(actions)} 个动作")
            return info, actions

        except Exception as e:
            logger.error(f"预测失败: {e}")
            import traceback

            traceback.print_exc()

            # 返回默认值
            return {
                "error": str(e),
                "full_plan": "Error occurred during prediction",
            }, []


class AgentS25_DSPy(AgentS2_5_DSPy):
    """AgentS2_5_DSPy 的别名，方便使用"""

    pass
