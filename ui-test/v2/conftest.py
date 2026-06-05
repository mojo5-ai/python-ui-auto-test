#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v2 Playwright conftest

提供 page/browser/context fixtures,让 v2 测试不用自己启浏览器。
pytest-playwright 自带 page fixture,我们这里额外加:
  - browser: 整个 session 共用一个浏览器
  - context: 每个 test 一个 context (隔离 cookies/storage)
  - v2_assembler: 包了 v1 Assembler 习惯用法的薄壳(给老代码迁移用)
"""
import pytest

# 不在 conftest 里 import v2.* — 让 fixture 在被请求时才 import,
# 避免"没装 playwright"时整个 conftest 加载失败。
# 这是为了兼容 v1 (Selenium) 测试也用 pytest 跑时不会挂。


@pytest.fixture(scope="session")
def v2_browser(request):
    """
    整个测试会话共用一个浏览器。
    用法: 直接用 pytest-playwright 自带的 browser fixture 也行,
    这个只是别名,让代码读起来更清楚这是 v2 的。
    """
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        # headless 默认 True (CI 友好)
        # 本地调试可以改 False 看浏览器
        headless = request.config.getini("v2_headless") if hasattr(request.config, 'getini') else True
        try:
            headless = request.config.getoption("--headed")
            headless = not bool(headless)
        except Exception:
            pass
        browser_name = "chromium"
        if browser_name == "chromium":
            browser = pw.chromium.launch(headless=headless)
        elif browser_name == "firefox":
            browser = pw.firefox.launch(headless=headless)
        elif browser_name == "webkit":
            browser = pw.webkit.launch(headless=headless)
        else:
            raise ValueError(f"unknown browser: {browser_name}")
        yield browser
        browser.close()


@pytest.fixture
def v2_context(v2_browser):
    """每个测试一个独立 context(隔离 cookies/storage)"""
    ctx = v2_browser.new_context(viewport={"width": 1920, "height": 1080})
    yield ctx
    ctx.close()


@pytest.fixture
def v2_page(v2_context):
    """每个测试一个 page"""
    page = v2_context.new_page()
    yield page
    page.close()


@pytest.fixture
def v2_assembler():
    """
    给习惯 v1 Assembler 写法的开发者用的薄壳 fixture。
    用法:
        def test_xxx(v2_assembler):
            page = v2_assembler.get_page()
            page.goto(...)
    """
    from v2.base.assembler import Assembler
    asm = Assembler(headless=True)
    yield asm
    asm.disassemble_all()
