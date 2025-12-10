"""
DSPy-based Agent-S2.5 Implementation
使用 DSPy 框架实现的 GUI 智能体
"""

__version__ = "0.1.0"

# 导出主要类，方便使用
from dspy_s25.agents.agent_s import AgentS2_5_DSPy, AgentS25_DSPy, UIAgent
from dspy_s25.agents.grounding import OSWorldACI, ACI
from dspy_s25.agents.worker import DSpyWorker
from dspy_s25.core.modules import (
    ActionGenerator,
    TrajectoryReflector,
    GroundingModule,
    MultiModalLMWrapper,
)
from dspy_s25.core.signatures import (
    ActionGenerationSignature,
    TrajectoryReflectionSignature,
    GroundingSignature,
)

__all__ = [
    # Agent 类
    "AgentS2_5_DSPy",
    "AgentS25_DSPy",
    "UIAgent",
    # Grounding
    "OSWorldACI",
    "ACI",
    # Worker
    "DSpyWorker",
    # DSPy Modules
    "ActionGenerator",
    "TrajectoryReflector",
    "GroundingModule",
    "MultiModalLMWrapper",
    # DSPy Signatures
    "ActionGenerationSignature",
    "TrajectoryReflectionSignature",
    "GroundingSignature",
]
