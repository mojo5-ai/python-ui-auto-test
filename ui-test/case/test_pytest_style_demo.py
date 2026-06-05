#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
示例：纯 pytest 风格测试（不依赖 unittest / selenium driver）

2026-06 新增。展示 pytest 风格怎么写：
  - 不用 class
  - 用 @pytest.fixture 拿依赖
  - 用 assert 写断言
  - 用 parametrize 跑多组数据

跑法：
  pytest case/test_pytest_style_demo.py -v
"""
import pytest
from util.config_reader import ConfigReader


# ─────────────────────────────────────────────────────────────────────
# 简单测试：不需要浏览器 / 装配器
# ─────────────────────────────────────────────────────────────────────
def test_config_reader_can_read_project_section():
    """[project] 段必须可读"""
    cfg = ConfigReader().read("project")
    assert "driver" in cfg
    assert cfg["driver"].lower() in ("chrome", "firefox", "ie", "edge", "opera", "safari")


def test_config_reader_can_read_html_section():
    """[html] 段必须含 cover_allowed,只能是 Y/N"""
    cfg = ConfigReader().read("html")
    assert cfg["cover_allowed"].upper() in ("Y", "N")


# ─────────────────────────────────────────────────────────────────────
# 参数化：同一段配置多种合法 driver 都应能读
# ─────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("driver_name", ["chrome", "firefox", "ie", "edge", "opera", "safari"])
def test_supported_drivers_listed_in_config(driver_name, project_config):
    """配置里至少要有一个合法 driver（这条不会真去启动浏览器）"""
    # project_config 是 fixture
    assert isinstance(project_config, dict)
    assert project_config["driver"]  # 至少非空


# ─────────────────────────────────────────────────────────────────────
# 跳过测试示例（演示 marker 工作）
# ─────────────────────────────────────────────────────────────────────
@pytest.mark.skip(reason="演示 pytest.skip — 跳过非关键验证")
def test_placeholder_skip():
    assert False  # 这条永不执行


@pytest.mark.xfail(reason="演示 pytest.xfail — 预期失败")
def test_placeholder_xfail():
    assert 1 == 2  # 这条预期失败


# ─────────────────────────────────────────────────────────────────────
# 标记分组
# ─────────────────────────────────────────────────────────────────────
@pytest.mark.smoke
def test_smoke_marker_works():
    """smoke 标签 — 跑 pytest -m smoke 时这条会被选中"""
    assert True


@pytest.mark.regression
def test_regression_marker_works():
    """regression 标签"""
    assert True
