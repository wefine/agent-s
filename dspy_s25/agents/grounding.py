"""
Grounding Agent - 将描述性动作转换为具体的屏幕坐标
基于 DSPy 实现的 ACI (Agent Computer Interaction) 接口
"""

import logging
import re
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import pyautogui
import pytesseract
from PIL import Image
from pytesseract import Output

logger = logging.getLogger("desktopenv.agent")


class ACI:
    """Agent Computer Interaction 基础类"""

    def __init__(self):
        self.notes: List[str] = []  # 文本缓冲区


def agent_action(func):
    """Agent 动作装饰器，标记可用的动作方法"""
    func.is_agent_action = True
    return func


class OSWorldACI(ACI):
    """
    基于 DSPy 的 OSWorld Agent Computer Interaction 实现
    处理屏幕交互和坐标转换
    """

    def __init__(
        self,
        platform: str = "linux",
        engine_params_for_generation: Optional[Dict] = None,
        engine_params_for_grounding: Optional[Dict] = None,
        width: int = 1920,
        height: int = 1080,
    ):
        """
        初始化 Grounding Agent

        Args:
            platform: 操作系统平台 (linux, darwin, windows)
            engine_params_for_generation: 生成模型的配置参数
            engine_params_for_grounding: Grounding 模型的配置参数
            width: 屏幕宽度
            height: 屏幕高度
        """
        super().__init__()
        self.platform = platform
        self.width = width
        self.height = height
        self.engine_params_generation = engine_params_for_generation or {}
        self.engine_params_grounding = engine_params_for_grounding or {}

        # 用于存储 OCR 提取的文本和坐标
        self.text_coordinates = {}

        logger.info(f"初始化 OSWorldACI: platform={platform}, size={width}x{height}")

    def extract_text_from_screenshot(
        self, screenshot_bytes: bytes
    ) -> Dict[int, Tuple[str, int, int]]:
        """
        使用 OCR 从截图中提取文本和坐标

        Args:
            screenshot_bytes: 截图的字节数据

        Returns:
            字典: {word_id: (text, x, y)}
        """
        try:
            image = Image.open(BytesIO(screenshot_bytes))

            # 使用 pytesseract 进行 OCR
            ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT)

            text_coords = {}
            word_id = 0

            for i in range(len(ocr_data["text"])):
                text = ocr_data["text"][i].strip()
                if text:  # 只保留非空文本
                    x = ocr_data["left"][i] + ocr_data["width"][i] // 2
                    y = ocr_data["top"][i] + ocr_data["height"][i] // 2
                    text_coords[word_id] = (text, x, y)
                    word_id += 1

            self.text_coordinates = text_coords
            logger.info(f"从截图中提取了 {len(text_coords)} 个文本元素")
            return text_coords

        except Exception as e:
            logger.error(f"OCR 提取失败: {e}")
            return {}

    def find_text_coordinates(self, description: str) -> Optional[Tuple[int, int]]:
        """
        根据描述查找文本的屏幕坐标

        Args:
            description: UI 元素的文本描述

        Returns:
            (x, y) 坐标元组，如果未找到返回 None
        """
        if not self.text_coordinates:
            logger.warning("没有可用的文本坐标数据")
            return None

        # 简单的文本匹配策略
        description_lower = description.lower()
        best_match = None
        best_score = 0

        for word_id, (text, x, y) in self.text_coordinates.items():
            text_lower = text.lower()

            # 完全匹配
            if description_lower in text_lower or text_lower in description_lower:
                score = len(text)
                if score > best_score:
                    best_score = score
                    best_match = (x, y)

        if best_match:
            logger.info(f"找到匹配: '{description}' -> {best_match}")
        else:
            logger.warning(f"未找到匹配: '{description}'")

        return best_match

    def assign_coordinates(self, plan: str, obs: Dict) -> str:
        """
        为计划中的描述性动作分配具体坐标

        Args:
            plan: 包含动作的计划文本
            obs: 观察数据，包含 screenshot

        Returns:
            更新后的计划文本
        """
        # 提取截图中的文本坐标
        if "screenshot" in obs:
            self.extract_text_from_screenshot(obs["screenshot"])

        return plan

    @agent_action
    def click(self, description: str, clicks: int = 1, button: str = "left"):
        """
        点击指定描述的 UI 元素

        Args:
            description: UI 元素的文本描述
            clicks: 点击次数
            button: 鼠标按钮 ("left", "right", "middle")
        """
        coords = self.find_text_coordinates(description)
        if coords:
            x, y = coords
            pyautogui.click(x, y, clicks=clicks, button=button)
            logger.info(f"点击: {description} at ({x}, {y})")
        else:
            logger.warning(f"无法定位: {description}，使用屏幕中心")
            pyautogui.click(
                self.width // 2, self.height // 2, clicks=clicks, button=button
            )

    @agent_action
    def double_click(self, description: str, button: str = "left"):
        """双击指定的 UI 元素"""
        self.click(description, clicks=2, button=button)

    @agent_action
    def right_click(self, description: str):
        """右键点击指定的 UI 元素"""
        self.click(description, clicks=1, button="right")

    @agent_action
    def type(self, text: str):
        """
        输入文本

        Args:
            text: 要输入的文本
        """
        pyautogui.write(text, interval=0.05)
        self.notes.append(text)
        logger.info(f"输入文本: {text}")

    @agent_action
    def hotkey(self, *keys):
        """
        按下组合键

        Args:
            *keys: 按键序列，例如 'ctrl', 'c'
        """
        pyautogui.hotkey(*keys)
        logger.info(f"热键: {'+'.join(keys)}")

    @agent_action
    def scroll(self, description: str, clicks: int = -3):
        """
        在指定位置滚动

        Args:
            description: 滚动区域的描述
            clicks: 滚动量 (负数向上，正数向下)
        """
        coords = self.find_text_coordinates(description)
        if coords:
            x, y = coords
            pyautogui.moveTo(x, y)

        pyautogui.scroll(clicks)
        logger.info(f"滚动: {clicks} at {description}")

    @agent_action
    def drag(self, start_description: str, end_description: str, button: str = "left"):
        """
        从起始位置拖动到结束位置

        Args:
            start_description: 起始位置描述
            end_description: 结束位置描述
            button: 鼠标按钮
        """
        start_coords = self.find_text_coordinates(start_description)
        end_coords = self.find_text_coordinates(end_description)

        if start_coords and end_coords:
            pyautogui.moveTo(*start_coords)
            pyautogui.drag(
                end_coords[0] - start_coords[0],
                end_coords[1] - start_coords[1],
                button=button,
                duration=0.5,
            )
            logger.info(f"拖动: {start_description} -> {end_description}")
        else:
            logger.warning(f"无法定位拖动坐标")

    @agent_action
    def wait(self, seconds: float):
        """
        等待指定秒数

        Args:
            seconds: 等待时间（秒）
        """
        import time

        time.sleep(seconds)
        logger.info(f"等待: {seconds} 秒")

    @agent_action
    def done(self):
        """标记任务完成"""
        logger.info("任务完成")
        return "DONE"

    @agent_action
    def fail(self):
        """标记任务失败"""
        logger.info("任务失败")
        return "FAIL"
