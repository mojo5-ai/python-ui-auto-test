#!/usr/bin/env python
"""
v2 运行入口

跟 v1 suite/run_all.py 对应,但用 pytest 跑 v2/case/

用法:
  python v2/run.py                         # 跑全部 v2 case (默认 no_browser only)
  python v2/run.py --all                   # 跑全部,包括需要浏览器的
  python v2/run.py -m no_browser           # 跑 no_browser 标签的(不需要装浏览器)
  python v2/run.py case/test_baidu_search.py  # 跑单个文件
  python v2/run.py -m ui --headed          # 跑 UI 测试 + 弹出浏览器(本地调试)

第一次跑 UI 测试需要先装浏览器:
  v2-venv/Scripts/playwright install chromium
"""
import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("args", nargs="*", help="传给 pytest 的参数")
    parser.add_argument("--all", action="store_true", help="跑全部,包括 UI")
    args = parser.parse_args()

    # 切到 ui-test/v2/ 目录
    v2_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(v2_dir)

    # 拼 pytest 参数
    pytest_args = list(args.args)
    if not pytest_args:
        # 默认只跑 no_browser,避免没装浏览器时挂
        pytest_args = ["case/", "-m", "no_browser"]
    elif "--all" in pytest_args:
        pytest_args.remove("--all")
        pytest_args += ["case/"]

    # 调 pytest
    import pytest
    sys.exit(pytest.main(pytest_args))


if __name__ == "__main__":
    main()
