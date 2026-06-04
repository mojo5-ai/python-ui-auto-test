"""
v2 不需要浏览器的 demo 测试 — 验证 v2 框架本身

跑法(不需要 playwright 装浏览器):
  pytest v2/case/test_baidu_demo.py -v
  pytest v2/case/test_baidu_demo.py -m no_browser
"""
import pytest

from v2.data.baidu_main_data import BaiduMainData
from v2.locator.baidu_main_locator import BaiduMainLocator
from v2.util.config_reader import ConfigReader


@pytest.mark.no_browser
def test_baidu_data_class_loads():
    """v2 data dataclass 可正常 import 和实例化"""
    d = BaiduMainData()
    assert d.url.startswith("https://")
    assert isinstance(d.data, str) and len(d.data) > 0


@pytest.mark.no_browser
def test_baidu_locator_loads():
    """v2 locator 用 CSS selector(不是 xpath)"""
    loc = BaiduMainLocator()
    # 验证不是 xpath
    assert not loc.search_input.startswith("/")
    assert not loc.search_input.startswith("(")
    # 验证是合理的 CSS selector
    assert any(c in loc.search_input for c in ["#", ".", "[", ">", " "])


@pytest.mark.no_browser
def test_config_reader_v2():
    """v2 配置读取器能读 [project] 段"""
    cfg = ConfigReader().read("project")
    assert "driver" in cfg
    assert "env" in cfg


@pytest.mark.no_browser
def test_page_common_class_exists():
    """v2 页面基类有 click / fill / goto / locator 等方法"""
    from v2.common.page_common import PageCommon
    methods = [m for m in dir(PageCommon) if not m.startswith("_")]
    for need in ("click", "fill", "goto", "locator", "screenshot_on_failure"):
        assert need in methods, f"PageCommon missing method: {need}"


@pytest.mark.no_browser
def test_assembler_class_exists():
    """v2 装配器有 get_page / disassemble_all 方法"""
    from v2.base.assembler import Assembler
    methods = [m for m in dir(Assembler) if not m.startswith("_")]
    for need in ("get_page", "get_context", "get_browser", "disassemble_all"):
        assert need in methods, f"Assembler missing method: {need}"
