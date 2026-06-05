"""
v2 截图工具

跟 v1 util/screenshot_tool.py 同样的功能,但用 Playwright 写
不用 WebDriver.get_screenshot_as_file
"""
import os
from datetime import datetime
from playwright.sync_api import Page


class ScreenshotTool:
    """截图工具,失败时调用"""

    def __init__(self, page: Page):
        self.page = page

    def save(self, name: str, output_dir: str = None) -> str:
        """
        保存截图到 output_dir,文件名 = name + 时间戳.png
        :return: 绝对路径
        """
        if output_dir is None:
            # 默认: ui-test/report/img/
            ui_test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            output_dir = os.path.join(ui_test_dir, "report", "img")
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        full_path = os.path.join(output_dir, filename)

        self.page.screenshot(path=full_path, full_page=True)
        return full_path
