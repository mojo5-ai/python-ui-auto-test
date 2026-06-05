"""
v2 页面基类

替代 v1 common/page_common.py。

v1 的痛点:
  - WebDriverWait 显式等待(10s 超时)
  - find_element_by_xpath 重复写
  - click/input 要写两遍

v2 的优势:
  - Playwright 的 locator.click() 自动等到元素可点击
  - page.fill() 自动等输入框就绪
  - 选择器只写一次
"""
from playwright.sync_api import Page, Locator

from v2.util.screenshot_tool import ScreenshotTool


class PageCommon:
    """所有页面类的基类

    子类用法:
        class BaiduMainPage(PageCommon):
            def jump_to(self):
                self.page.goto("https://www.baidu.com")
            def search(self, keyword):
                self.fill("#kw", keyword)
                self.click("#su")
    """

    def __init__(self, page: Page):
        self.page = page
        self.screenshot = ScreenshotTool(page)

    # ── 元素操作(全部自动等待) ─────────────────────────────
    def click(self, selector: str, **kwargs):
        """点元素,自动等到可点击 + 稳定"""
        self.locator(selector).click(**kwargs)

    def fill(self, selector: str, value: str, **kwargs):
        """填输入框,自动等可编辑"""
        self.locator(selector).fill(value, **kwargs)

    def get_text(self, selector: str) -> str:
        """读元素文本,自动等可见"""
        return self.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        """元素是否可见(不抛异常)"""
        return self.locator(selector).is_visible()

    def locator(self, selector: str) -> Locator:
        """直接拿 Locator 对象(更高级用法)"""
        return self.page.locator(selector)

    # ── 页面级操作 ───────────────────────────────────
    def goto(self, url: str, **kwargs):
        """打开 URL,Playwright 默认等到 'load' 事件"""
        self.page.goto(url, **kwargs)

    def wait_for_url(self, url_pattern: str, **kwargs):
        """等 URL 匹配"""
        self.page.wait_for_url(url_pattern, **kwargs)

    def screenshot_on_failure(self, name: str):
        """出错时截图(在 fixture 里调)"""
        self.screenshot.save(name)
