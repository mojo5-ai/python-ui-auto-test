"""
v2 百度数据
"""
from dataclasses import dataclass


@dataclass
class BaiduMainData:
    """百度首页数据"""
    url: str = "https://www.baidu.com"
    data: str = "Python Playwright"
