"""
Worker Agent - 使用 DSPy 实现的工作代理
负责生成和执行具体的 GUI 操作动作
"""

import logging
import textwrap
from typing import Dict, List, Tuple, Optional

import dspy

from dspy_s25.agents.grounding import ACI
from dspy_s25.core.modules import (
    ActionGenerator,
    TrajectoryReflector,
    MultiModalLMWrapper,
)
from dspy_s25.memory.procedural_memory import PROCEDURAL_MEMORY
from dspy_s25.utils.common_utils import (
    call_dspy_module_safe,
    parse_single_code_from_string,
    sanitize_code,
    extract_first_agent_function,
    format_action_history,
)

logger = logging.getLogger("desktopenv.agent")


class DSpyWorker:
    """
    基于 DSPy 的 Worker Agent
    管理动作生成、反思和历史记录
    """

    def __init__(
        self,
        engine_params: Dict,
        grounding_agent: ACI,
        platform: str = "linux",
        max_trajectory_length: int = 8,
        enable_reflection: bool = True,
    ):
        """
        初始化 Worker

        Args:
            engine_params: 语言模型配置参数
            grounding_agent: Grounding Agent 实例
            platform: 操作系统平台
            max_trajectory_length: 最大轨迹长度
            enable_reflection: 是否启用反思功能
        """
        self.engine_params = engine_params
        self.grounding_agent = grounding_agent
        self.platform = platform
        self.max_trajectory_length = max_trajectory_length
        self.enable_reflection = enable_reflection

        # 初始化语言模型
        self.lm_wrapper = MultiModalLMWrapper(engine_params)

        # 初始化 DSPy 模块
        self.action_generator = ActionGenerator(use_cot=True)

        if self.enable_reflection:
            self.trajectory_reflector = TrajectoryReflector(use_cot=True)

        # 状态变量
        self.turn_count = 0
        self.worker_history = []
        self.reflections = []
        self.screenshot_inputs = []

        logger.info(
            f"DSpyWorker 初始化完成: "
            f"platform={platform}, "
            f"max_trajectory={max_trajectory_length}, "
            f"reflection={'启用' if enable_reflection else '禁用'}"
        )

    def reset(self):
        """重置 Worker 状态"""
        self.turn_count = 0
        self.worker_history = []
        self.reflections = []
        self.screenshot_inputs = []
        logger.info("Worker 状态已重置")

    def get_reflection(
        self, instruction: str, current_screenshot_desc: str
    ) -> Optional[str]:
        """
        生成对当前轨迹的反思

        Args:
            instruction: 任务指令
            current_screenshot_desc: 当前截图描述

        Returns:
            反思内容字符串
        """
        if not self.enable_reflection or self.turn_count == 0:
            return None

        try:
            # 格式化当前轨迹
            trajectory = format_action_history(self.worker_history)
            last_action = (
                self.worker_history[-1] if self.worker_history else "No action"
            )

            # 调用反思模块
            reflection_result = call_dspy_module_safe(
                self.trajectory_reflector,
                task_description=instruction,
                current_trajectory=trajectory,
                last_action=last_action,
            )

            reflection = reflection_result.reflection
            self.reflections.append(reflection)

            logger.info(f"反思生成: {reflection[:100]}...")
            return reflection

        except Exception as e:
            logger.error(f"反思生成失败: {e}")
            return None

    def generate_next_action(
        self,
        instruction: str,
        obs: Dict,
    ) -> Tuple[Dict, List]:
        """
        生成下一步动作

        Args:
            instruction: 任务指令
            obs: 观察数据 (包含 screenshot)

        Returns:
            (info_dict, action_list) 元组
            - info_dict: 包含计划、反思等信息的字典
            - action_list: 可执行的动作列表
        """
        agent = self.grounding_agent

        # 构建当前状态描述
        if self.turn_count == 0:
            screenshot_desc = "初始屏幕，尚未执行任何动作"
        else:
            screenshot_desc = "当前屏幕状态"

        # 获取反思
        reflection = ""
        if self.enable_reflection and self.turn_count > 0:
            reflection = self.get_reflection(instruction, screenshot_desc) or ""
            if reflection:
                reflection = f"REFLECTION: {reflection}"

        # 格式化动作历史
        action_history = format_action_history(self.worker_history)
        if self.turn_count == 0:
            action_history = "初始状态，没有历史动作"

        # 格式化文本缓冲区
        text_buffer = f"[{','.join(agent.notes)}]" if agent.notes else "[]"

        try:
            # 调用动作生成器
            logger.info(f"\n{'='*60}")
            logger.info(f"Step {self.turn_count + 1}: 生成下一步动作")
            logger.info(f"任务: {instruction}")
            logger.info(f"文本缓冲: {text_buffer}")
            logger.info(f"{'='*60}\n")

            # 注意：这里简化处理，实际应该将图像传递给模型
            # DSPy 目前对多模态支持有限，这里先用文本描述代替
            action_result = call_dspy_module_safe(
                self.action_generator,
                task_description=instruction,
                screenshot_analysis=screenshot_desc,
                action_history=action_history,
                reflection=reflection,
                text_buffer=text_buffer,
            )

            # 提取结果
            plan = action_result.grounded_action_code
            full_response = (
                f"(Previous Action Verification)\n{action_result.previous_action_verification}\n\n"
                f"(Screenshot Analysis)\n{action_result.current_state_analysis}\n\n"
                f"(Next Action)\n{action_result.next_action_description}\n\n"
                f"(Grounded Action)\n{action_result.grounded_action_code}"
            )

            self.worker_history.append(full_response)
            logger.info(f"完整计划:\n{full_response}\n")

            # 使用 Grounding Agent 转换坐标
            agent.assign_coordinates(plan, obs)

            # 解析代码
            plan_code = parse_single_code_from_string(plan)
            plan_code = sanitize_code(plan_code)
            plan_code = extract_first_agent_function(plan_code)

            if plan_code:
                exec_code = eval(plan_code)
            else:
                logger.warning("无法解析动作代码，默认等待")
                exec_code = eval("agent.wait(1.0)")

            # 构建返回信息
            executor_info = {
                "full_plan": full_response,
                "executor_plan": plan,
                "plan_code": plan_code,
                "reflection": reflection,
                "previous_verification": action_result.previous_action_verification,
                "current_analysis": action_result.current_state_analysis,
                "next_action_desc": action_result.next_action_description,
            }

            # 更新状态
            self.turn_count += 1
            self.screenshot_inputs.append(obs.get("screenshot"))

            # 管理历史长度
            if len(self.worker_history) > self.max_trajectory_length:
                self.worker_history.pop(0)
            if len(self.screenshot_inputs) > self.max_trajectory_length:
                self.screenshot_inputs.pop(0)

            return executor_info, [exec_code]

        except Exception as e:
            logger.error(f"动作生成失败: {e}")
            import traceback

            traceback.print_exc()

            # 返回默认等待动作
            return {
                "full_plan": "Error occurred",
                "executor_plan": "agent.wait(1.0)",
                "plan_code": "agent.wait(1.0)",
                "reflection": "",
                "error": str(e),
            }, [eval("agent.wait(1.0)")]
