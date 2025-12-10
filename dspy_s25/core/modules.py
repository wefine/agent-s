"""
DSPy Modules for GUI Agent
使用 DSPy 的 Module 和 Predict 构建的核心模块
"""

import dspy
from typing import Dict, Any, Optional

from dspy_s25.core.signatures import (
    ActionGenerationSignature,
    TrajectoryReflectionSignature,
    GroundingSignature,
)


class ActionGenerator(dspy.Module):
    """动作生成器: 基于当前状态和历史生成下一步动作"""

    def __init__(self, use_cot: bool = True):
        """
        Args:
            use_cot: 是否使用思维链 (Chain of Thought)
        """
        super().__init__()
        if use_cot:
            self.generate = dspy.ChainOfThought(ActionGenerationSignature)
        else:
            self.generate = dspy.Predict(ActionGenerationSignature)

    def forward(
        self,
        task_description: str,
        screenshot_analysis: str,
        action_history: str,
        reflection: str = "",
        text_buffer: str = "",
    ) -> dspy.Prediction:
        """
        生成下一步动作

        Returns:
            dspy.Prediction 包含:
                - previous_action_verification
                - current_state_analysis
                - next_action_description
                - grounded_action_code
        """
        return self.generate(
            task_description=task_description,
            screenshot_analysis=screenshot_analysis,
            action_history=action_history,
            reflection=reflection,
            text_buffer=text_buffer,
        )


class TrajectoryReflector(dspy.Module):
    """轨迹反思器: 分析任务执行轨迹，检测问题并提供建议"""

    def __init__(self, use_cot: bool = True):
        """
        Args:
            use_cot: 是否使用思维链
        """
        super().__init__()
        if use_cot:
            self.reflect = dspy.ChainOfThought(TrajectoryReflectionSignature)
        else:
            self.reflect = dspy.Predict(TrajectoryReflectionSignature)

    def forward(
        self,
        task_description: str,
        current_trajectory: str,
        last_action: str,
    ) -> dspy.Prediction:
        """
        对轨迹进行反思

        Returns:
            dspy.Prediction 包含:
                - reflection: 反思结果
        """
        return self.reflect(
            task_description=task_description,
            current_trajectory=current_trajectory,
            last_action=last_action,
        )


class GroundingModule(dspy.Module):
    """坐标定位模块: 将描述性文本转换为具体的屏幕坐标"""

    def __init__(self, use_cot: bool = True):
        """
        Args:
            use_cot: 是否使用思维链
        """
        super().__init__()
        if use_cot:
            self.ground = dspy.ChainOfThought(GroundingSignature)
        else:
            self.ground = dspy.Predict(GroundingSignature)

    def forward(
        self,
        phrase: str,
        text_table: str,
        screenshot_context: str = "",
    ) -> dspy.Prediction:
        """
        定位文本描述对应的坐标

        Returns:
            dspy.Prediction 包含:
                - reasoning: 推理过程
                - word_id: 单词ID
        """
        return self.ground(
            phrase=phrase,
            text_table=text_table,
            screenshot_context=screenshot_context,
        )


class MultiModalLMWrapper:
    """
    多模态语言模型包装器
    用于处理包含图像和文本的输入
    """

    def __init__(self, lm_config: Dict[str, Any]):
        """
        Args:
            lm_config: 语言模型配置
                - engine_type: 模型类型 (openai, anthropic, etc.)
                - model: 模型名称
                - api_key: API密钥
                - base_url: API基础URL (可选)
                - temperature: 温度参数 (可选)
        """
        self.lm_config = lm_config
        self.engine_type = lm_config.get("engine_type", "openai")
        self.model = lm_config.get("model")
        self.api_key = lm_config.get("api_key")
        self.base_url = lm_config.get("base_url")
        self.temperature = lm_config.get("temperature", 0.0)

        self._initialize_lm()

    def _initialize_lm(self):
        """初始化语言模型"""
        # DSPy 3.x 使用 dspy.LM 作为统一接口
        try:
            if self.engine_type in ["openai", "open_router"]:
                # OpenAI 和 OpenRouter (OpenAI 兼容)
                self.lm = dspy.LM(
                    model=self.model,
                    api_key=self.api_key,
                    api_base=self.base_url if self.base_url else None,
                )
            elif self.engine_type == "anthropic":
                # Anthropic Claude
                self.lm = dspy.LM(
                    model=f"anthropic/{self.model}",
                    api_key=self.api_key,
                )
            else:
                # 通用方式
                self.lm = dspy.LM(
                    model=self.model,
                    api_key=self.api_key,
                )

            # 配置 dspy
            dspy.configure(lm=self.lm)

        except Exception as e:
            # 如果 dspy.LM 不存在，尝试直接配置
            import warnings

            warnings.warn(f"无法初始化 DSPy LM: {e}. " "DSPy 配置可能需要手动设置。")
            self.lm = None

    def get_lm(self):
        """获取配置好的语言模型"""
        return self.lm
