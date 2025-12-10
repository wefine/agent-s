"""
通用工具函数
从 s2_5 移植的工具函数
"""

import re
import time
from typing import Tuple, Any


def call_dspy_module_safe(module: Any, max_retries: int = 3, **kwargs) -> Any:
    """
    安全调用 dspy 模块，带重试机制

    Args:
        module: dspy 模块实例
        max_retries: 最大重试次数
        **kwargs: 传递给模块的参数

    Returns:
        模块的预测结果
    """
    attempt = 0
    response = None

    while attempt < max_retries:
        try:
            response = module(**kwargs)
            assert response is not None, "Response from module should not be None"
            print(f"✓ DSPy 模块调用成功 (尝试 {attempt + 1}/{max_retries})")
            break
        except Exception as e:
            attempt += 1
            print(f"✗ 尝试 {attempt} 失败: {e}")
            if attempt == max_retries:
                print("达到最大重试次数，处理失败")
                raise
            time.sleep(1.0)

    return response


def parse_single_code_from_string(input_string: str) -> str:
    """
    从字符串中解析单个代码块

    Args:
        input_string: 包含代码的字符串

    Returns:
        解析出的代码字符串
    """
    input_string = input_string.strip()
    if input_string.strip() in ["WAIT", "DONE", "FAIL"]:
        return input_string.strip()

    # 匹配 ```code``` 或 ```python code``` 格式
    pattern = r"```(?:\w+\s+)?(.*?)```"
    matches = re.findall(pattern, input_string, re.DOTALL)

    codes = []

    for match in matches:
        match = match.strip()
        commands = ["WAIT", "DONE", "FAIL"]

        if match in commands:
            codes.append(match.strip())
        elif match.split("\n")[-1] in commands:
            if len(match.split("\n")) > 1:
                codes.append("\n".join(match.split("\n")[:-1]))
            codes.append(match.split("\n")[-1])
        else:
            codes.append(match)

    if len(codes) <= 0:
        return "fail"
    return codes[0]


def sanitize_code(code: str) -> str:
    """
    清理代码中的引号

    Args:
        code: 原始代码字符串

    Returns:
        清理后的代码字符串
    """
    if "\n" in code:
        pattern = r'(".*?")'
        matches = re.findall(pattern, code, flags=re.DOTALL)
        if matches:
            first_match = matches[0]
            code = code.replace(first_match, f'"""{first_match[1:-1]}"""', 1)
    return code


def extract_first_agent_function(code_string: str) -> str:
    """
    从代码字符串中提取第一个 agent 函数调用

    Args:
        code_string: 包含代码的字符串

    Returns:
        第一个 agent 函数调用，如果没找到返回 None
    """
    # 匹配 agent.xxx() 格式的函数调用
    pattern = r'agent\.[a-zA-Z_]+\((?:[^()\'"]|\'[^\']*\'|"[^"]*")*\)'
    matches = re.findall(pattern, code_string)
    return matches[0] if matches else None


def split_thinking_response(full_response: str) -> Tuple[str, str]:
    """
    从完整响应中分离思考过程和答案
    用于支持某些模型的思考标签

    Args:
        full_response: 完整的响应字符串

    Returns:
        (答案, 思考过程) 元组
    """
    try:
        # 提取 thoughts 部分
        thoughts_match = re.search(
            r"<thoughts>(.*?)</thoughts>", full_response, re.DOTALL
        )
        thoughts = thoughts_match.group(1).strip() if thoughts_match else ""

        # 提取 answer 部分
        answer_match = re.search(r"<answer>(.*?)</answer>", full_response, re.DOTALL)
        answer = answer_match.group(1).strip() if answer_match else full_response

        return answer, thoughts
    except Exception as e:
        return full_response, ""


def format_action_history(history: list, max_length: int = 5) -> str:
    """
    格式化动作历史为字符串

    Args:
        history: 动作历史列表
        max_length: 最大保留长度

    Returns:
        格式化的历史字符串
    """
    if not history:
        return "No previous actions"

    recent_history = history[-max_length:] if len(history) > max_length else history
    formatted = []

    for i, action in enumerate(recent_history, 1):
        formatted.append(f"Step {i}: {action}")

    return "\n".join(formatted)


def encode_image_to_base64(image_bytes: bytes) -> str:
    """
    将图像字节编码为 base64 字符串

    Args:
        image_bytes: 图像的字节数据

    Returns:
        base64 编码的字符串
    """
    import base64

    return base64.b64encode(image_bytes).decode("utf-8")
