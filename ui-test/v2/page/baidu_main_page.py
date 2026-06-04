"""
v2 百度首页 - 页面对象

跟 v1 page/baidu_main_page.py 同样的功能,用 Playwright 写。
"""
from v2.common.page_common import PageCommon
from v2.data.baidu_main_data import BaiduMainData
from v2.locator.baidu_main_locator import BaiduMainLocator


class BaiduMainPage(PageCommon):
    """百度首页"""

    def jump_to(self):
        """打开百度首页,等到 networkidle (网络请求结束)"""
        self.goto(BaiduMainData.url, wait_until="networkidle")

    def search(self, keyword: str = None):
        """搜索关键词,默认用 data 里的值"""
        if keyword is None:
            keyword = BaiduMainData.data
        # v1 要写 WebDriverWait + find_element_by_xpath + click 三段
        # v2 两行搞定,自动等待
        self.fill(BaiduMainLocator.search_input, keyword)
        self.click(BaiduMainLocator.search_btn)
