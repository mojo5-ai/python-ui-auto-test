"""
v2 真实 UI 测试 — 百度搜索

跑这个需要装好浏览器:
  playwright install chromium

或者用 pytest-playwright 自动装:
  pytest --browser-install (如果该 flag 存在)
"""
import pytest

from v2.page.baidu_main_page import BaiduMainPage


@pytest.mark.ui
def test_baidu_search_python(v2_page):
    """打开百度 → 搜 'Python Playwright' → 验证结果页"""
    baidu = BaiduMainPage(v2_page)

    # 打开百度
    baidu.jump_to()

    # 验证标题含 "百度"
    assert "百度" in v2_page.title(), f"unexpected title: {v2_page.title()}"

    # 搜索
    baidu.search("Python Playwright")

    # 等到 URL 变成搜索结果页
    v2_page.wait_for_url("**/s**", timeout=10000)

    # 验证当前 URL 是搜索结果页
    assert "/s" in v2_page.url, f"expected search URL, got: {v2_page.url}"

    # 验证页面有搜索结果(简单粗暴,至少有输入框回显)
    # 百度搜索结果页搜索框 id 还是 kw
    assert v2_page.locator("#kw").count() > 0, "search input not found on results page"
