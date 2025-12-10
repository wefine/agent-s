"""
DSPy Signatures for GUI Agent
定义输入输出的结构化签名
"""

import dspy


class ActionGenerationSignature(dspy.Signature):
    """生成下一步 GUI 操作动作的签名"""

    # 输入字段
    task_description = dspy.InputField(desc="任务描述: 用户想要完成的任务")
    screenshot_analysis = dspy.InputField(desc="当前截图分析: 当前屏幕状态的详细描述")
    action_history = dspy.InputField(desc="历史动作: 之前执行过的动作和结果")
    reflection = dspy.InputField(desc="反思内容: 对当前轨迹的反思和建议", default="")
    text_buffer = dspy.InputField(desc="文本缓冲区: 当前记录的文本信息", default="")

    # 输出字段
    previous_action_verification = dspy.OutputField(
        desc="上一步动作验证: 分析上一步动作是否成功"
    )
    current_state_analysis = dspy.OutputField(
        desc="当前状态分析: 详细描述当前桌面和应用程序状态"
    )
    next_action_description = dspy.OutputField(
        desc="下一步动作: 用自然语言描述下一步要执行的动作"
    )
    grounded_action_code = dspy.OutputField(
        desc="具体动作代码: 使用 API 方法实现的 Python 代码"
    )


class TrajectoryReflectionSignature(dspy.Signature):
    """对任务轨迹进行反思的签名"""

    # 输入字段
    task_description = dspy.InputField(desc="任务描述: 用户想要完成的任务")
    current_trajectory = dspy.InputField(desc="当前轨迹: 包含历史动作和截图的完整轨迹")
    last_action = dspy.InputField(desc="最后一次动作: 最近执行的动作")

    # 输出字段
    reflection = dspy.OutputField(
        desc="反思结果: 分析轨迹是否正常，是否有循环，是否需要调整策略"
    )


class GroundingSignature(dspy.Signature):
    """将描述性动作转换为具体坐标的签名"""

    # 输入字段
    phrase = dspy.InputField(desc="描述性短语: 要点击或交互的UI元素的文本描述")
    text_table = dspy.InputField(desc="文本表格: 屏幕上所有文本及其ID的表格")
    screenshot_context = dspy.InputField(desc="截图上下文: 当前屏幕截图的描述")

    # 输出字段
    reasoning = dspy.OutputField(desc="推理过程: 为什么选择这个单词ID的推理")
    word_id = dspy.OutputField(desc="单词ID: 最相关的单词在文本表格中的唯一ID")
