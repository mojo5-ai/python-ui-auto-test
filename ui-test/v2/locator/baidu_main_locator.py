"""
v2 百度首页元素定位

注意:跟 v1 locator/baidu_main_locator.py 用的 xpath 不同
v2 优先用 CSS selector(更短更稳)
"""
from dataclasses import dataclass


@dataclass
class BaiduMainLocator:
    """百度首页元素定位"""
    # 搜索输入框: id="kw" 是百度搜索框
    search_input: str = "#kw"
    # 搜索按钮: id="su"
    search_btn: str = "#su"
