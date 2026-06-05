#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pytest 全局配置 / fixtures

2026-06 新增。让现有 unittest 风格的 case 也能在 pytest 下运行，
并提供几个常用的 fixture 减少重复代码。

本文件不修改任何业务代码 — pytest 原生支持 unittest.TestCase，
case 里的 setUp / tearDown / @paramunittest 全部自动识别。
"""
import os
import sys
import pytest


# ─────────────────────────────────────────────────────────────────────
# 路径处理：让 case/ 里的 `from base.xxx import ...` 能解析
# ─────────────────────────────────────────────────────────────────────
# pytest.ini 里已经写了 pythonpath = . ，这里再保险地强制加一次
# （某些 pytest 版本对 ini 的 pythonpath 处理有 bug）
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)


# ─────────────────────────────────────────────────────────────────────
# 项目级 fixtures
# ─────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def project_root():
    """返回 ui-test/ 目录的绝对路径"""
    return _THIS_DIR


@pytest.fixture(scope="session")
def config_reader():
    """
    提供 ConfigReader 单例。
    注意：ConfigReader 内部每次 read() 都重新读 ini 文件，所以这里
    只是为了让测试代码不用每次都 import。
    """
    # 延迟 import — 避免在 conftest 加载时触发 selenium 等重依赖
    from util.config_reader import ConfigReader
    return ConfigReader


@pytest.fixture
def project_config(config_reader):
    """
    返回 [project] 段的 dict，方便单测试读取 driver/env/lan/redis_enable 等。
    用法：
        def test_something(project_config):
            if project_config['redis_enable'].upper() == 'Y':
                ...
    """
    return config_reader().read("project")


@pytest.fixture
def driver_config(project_config):
    """返回 [driver] 段，决定该用什么浏览器"""
    return project_config  # driver 字段就在 [project] 里


@pytest.fixture
def skip_if_redis_disabled(project_config):
    """需要 redis 的测试可以这样声明：
        @pytest.mark.usefixtures('skip_if_redis_disabled')
        def test_xxx():
            ...
    """
    if project_config.get("redis_enable", "N").upper() != "Y":
        pytest.skip("redis_enable != 'Y' in config.ini")


@pytest.fixture
def skip_if_mysql_disabled(project_config):
    """需要 mysql 的测试可以这样声明"""
    if project_config.get("mysql_enable", "N").upper() != "Y":
        pytest.skip("mysql_enable != 'Y' in config.ini")


# ─────────────────────────────────────────────────────────────────────
# 自动 mark：根据文件名 / 类名打标签
# ─────────────────────────────────────────────────────────────────────
def pytest_collection_modifyitems(config, items):
    """
    收集完测试后，给它们自动打 marker。
    例如 test_other_case.py 里的 test_* 自动得到 'regression' 标签。
    """
    for item in items:
        # 根据文件路径打标签
        if "baidu" in item.fspath.basename:
            item.add_marker(pytest.mark.smoke)
        elif "csdn" in item.fspath.basename:
            item.add_marker(pytest.mark.regression)
        elif "other" in item.fspath.basename:
            item.add_marker(pytest.mark.regression)
            # TestOtherCase 里有一个故意失败的 assert False
            # 让它默认 xfail，不会污染测试结果
            if "TestOtherCase" in item.name:
                item.add_marker(pytest.mark.xfail(reason="故意失败,用于演示截图"))


# ─────────────────────────────────────────────────────────────────────
# 测试运行前的环境检查
# ─────────────────────────────────────────────────────────────────────
def pytest_configure(config):
    """
    pytest 启动时跑一次。这里打印一行 banner，让用户知道
    conftest 已经加载。
    """
    print("\n[conftest] pytest configured, ui-test/ added to sys.path")
    print(f"[conftest] project root: {_THIS_DIR}")


# ─────────────────────────────────────────────────────────────────────
# 钩子：让 unittest.TestCase 也能用 paramunittest 的参数
# ─────────────────────────────────────────────────────────────────────
# pytest 内置支持 unittest.TestCase，所以 @paramunittest 装饰的类
# 会被识别为一个测试类。但每个参数化后的 test_* 方法 pytest 不会
# 自动收集 — 因为 paramunittest 是在 unittest.TestCase.__init__
# 时动态加的。
#
# 简单解法：在 run_all.py / run_all_mutithread.py 里用 unittest 跑参数化用例；
# 单独想用 pytest 跑某个 case 时，直接 `pytest case/test_baidu_case.py -v` 即可。
# pytest 至少会跑那些非 paramunittest 的 test_* 方法 + 整个测试类一次。
