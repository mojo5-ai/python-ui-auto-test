"""
v2 Playwright 装配器

替代原 v1 base/assembler.py (Selenium 3 风格)。

核心差异:
  - 不用 WebDriver,直接用 Playwright 同步 API
  - 不用 chromedriver.exe,Playwright 自带 Chromium
  - 不用 ThreadLocalStorage,用 context 隔离(每个 page 一个 context)
  - 不用 WebDriverWait,Playwright 自动等待元素可见/可点击
"""
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from v2.util.config_reader import ConfigReader


class Assembler:
    """一个 Assembler = 一个 Browser + 一个 BrowserContext + 一个 Page

    用法:
        asm = Assembler()
        page = asm.get_page()
        page.goto(...)
        asm.disassemble_all()
    """

    def __init__(self, headless: bool = True, browser_name: str = None):
        """
        :param headless: 是否无头模式 (CI 通常 True,本地调试 False)
        :param browser_name: chrome / firefox / webkit,默认从 config 读
        """
        if browser_name is None:
            browser_name = ConfigReader().read("project")["driver"]

        self._pw = sync_playwright().start()
        self._browser: Browser = self._launch_browser(browser_name, headless)
        # viewport 跟 v1 一致,1920x1080
        self._context: BrowserContext = self._browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        self._page: Page = self._context.new_page()

    def _launch_browser(self, name: str, headless: bool) -> Browser:
        """根据名字启动对应浏览器"""
        name = name.lower()
        if name == "chrome" or name == "chromium":
            return self._pw.chromium.launch(headless=headless)
        elif name == "firefox":
            return self._pw.firefox.launch(headless=headless)
        elif name == "webkit" or name == "safari":
            return self._pw.webkit.launch(headless=headless)
        elif name == "edge":
            # Edge 跟 Chrome 都是 chromium 内核,用 channel 指定
            return self._pw.chromium.launch(headless=headless, channel="msedge")
        else:
            raise ValueError(
                f"Unsupported browser: {name}. "
                f"Playwright supports: chromium, firefox, webkit, edge."
            )

    # ── 装配(已经做完,只是 getter) ──────────────────────────
    def get_page(self) -> Page:
        return self._page

    def get_context(self) -> BrowserContext:
        return self._context

    def get_browser(self) -> Browser:
        return self._browser

    # ── 拆卸 ─────────────────────────────────────────────
    def disassemble_all(self):
        """反序关闭所有资源"""
        try:
            if self._page and not self._page.is_closed():
                self._page.close()
        except Exception:
            pass
        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._pw:
                self._pw.stop()
        except Exception:
            pass
