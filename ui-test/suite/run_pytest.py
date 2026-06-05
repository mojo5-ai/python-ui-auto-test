#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pytest 运行入口（2026-06 新增）

跟 run_all.py 并存。区别：
  - run_all.py        — 用 unittest + BeautifulReport 出报告
  - run_pytest.py     — 用 pytest 出报告（更现代，可以加各种插件）

跑法：
  python suite/run_pytest.py                    # 跑全部
  python suite/run_pytest.py case/test_baidu_case.py -v
  python suite/run_pytest.py -m smoke           # 跑 smoke 标记的
  python suite/run_pytest.py -k baidu           # 跑名字含 baidu 的
  python suite/run_pytest.py --html=report/html/pytest-report.html --self-contained-html
                                    # 出 pytest-html 报告（需要 pip install pytest-html）
"""
import os
import sys


def main():
    # 把 ui-test/ 目录加到 sys.path
    suite_dir = os.path.dirname(os.path.abspath(__file__))
    ui_test_dir = suite_dir[:suite_dir.find("python-ui-auto-test") + len("python-ui-auto-test")] + "/ui-test"
    sys.path.insert(0, ui_test_dir)

    # 切到 ui-test/ 目录（pytest.ini 在那里）
    os.chdir(ui_test_dir)

    # 收集用户传的参数
    args = sys.argv[1:] if len(sys.argv) > 1 else ["case/"]

    # 调用 pytest
    import pytest
    exit_code = pytest.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
