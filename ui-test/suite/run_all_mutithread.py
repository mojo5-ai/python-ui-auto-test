#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多线程运行入口（已修复报告互相覆盖的问题）。

2026-06 修复记录:
  - 之前: N 个线程用同一个 report_name,HTML 报告互相覆盖;遍历 TestSuite
          时拿到的是单个 TestCase 而不是 TestCase 组,导致 3 个线程都跑同一份
          用例且写同一份报告。
  - 修复: 把"整个测试套"分摊到 N 个线程上,每个线程拿到一个不相交的子集,
          并发执行完后,各自生成独立的 HTML 文件,文件名带线程后缀。
          BeautifulReport 内部非线程安全,用 ReportTool 的 _report_lock
          串行化"写 HTML 报告"这一段。
"""
import os
import threading
import unittest
from tomorrow import threads
from case import test_baidu_case, test_csdn_case, test_other_case
from util.config_reader import ConfigReader
from util.report_tool import ReportTool


# 并发线程数
THREAD_COUNT = 3


# 报告存放路径
report_path = os.path.abspath(os.path.dirname(__file__))[
              :os.path.abspath(os.path.dirname(__file__)).find("python-ui-auto-test") + len(
                  "python-ui-auto-test")] + "/ui-test" + ConfigReader().read("html")["htmlfile_path"]


# 基础报告名
report_name_base = ConfigReader().read("html")["htmlfile_name"]


# 每个线程拿到的测试套子集 + 各自的文件名
def _build_thread_tasks():
    """
    把全部用例平均切成 THREAD_COUNT 份，每份一个 TestSuite，每份独立 report filename。
    返回 [(thread_id, suite, report_filename), ...]
    """
    # 先收集全部测试模块
    loader = unittest.TestLoader()
    all_modules = [test_baidu_case, test_csdn_case, test_other_case]
    all_tests = []
    for m in all_modules:
        all_tests.extend(loader.loadTestsFromModule(m))

    # 报告基名（处理 cover_allowed=N 的情况）
    base_filename = ReportTool(suites=unittest.TestSuite()).get_html_name(
        filename=report_name_base + "-多线程",
        report_dir=report_path,
    )

    # 切片
    n = len(all_tests)
    chunk_size = (n + THREAD_COUNT - 1) // THREAD_COUNT  # 向上取整
    tasks = []
    for tid in range(THREAD_COUNT):
        start = tid * chunk_size
        end = min(start + chunk_size, n)
        if start >= n:
            # 用例不够分，这个线程不出任务
            continue
        sub_suite = unittest.TestSuite(all_tests[start:end])
        # 每个线程的报告名带 -T{thread_id} 后缀
        thread_filename = f"{base_filename}-T{tid + 1}"
        tasks.append((tid + 1, sub_suite, thread_filename))

    return tasks


# 单线程执行函数（被 @threads 装饰后变成"立即返回 Future"）
@threads(THREAD_COUNT)
def run_one_thread(thread_id, suite, filename):
    """
    单个线程的工作：跑分配的子套件，生成带线程号的独立报告。
    """
    print(f"[T{thread_id}] 启动, 分配 {suite.countTestCases()} 个用例, 报告名: {filename}")
    ReportTool(suite).run(
        filename=filename,
        description=f"多线程-T{thread_id}",
        report_dir=report_path,
        theme="theme_cyan",
    )
    print(f"[T{thread_id}] 完成, 报告: {report_path}{filename}.html")


def main():
    """
    主流程：建任务 -> 并发跑 -> 等待所有线程结束。
    """
    tasks = _build_thread_tasks()
    if not tasks:
        print("没有可执行的测试用例")
        return

    print(f"=== 多线程模式启动: {len(tasks)} 线程, 共 {sum(s.countTestCases() for _, s, _ in tasks)} 用例 ===")

    # tomorrow 的 @threads 装饰器返回的是一个 list 形式
    # 但这里我们直接调函数拿到 Future 列表，更可控
    futures = []
    for tid, suite, filename in tasks:
        futures.append(run_one_thread(tid, suite, filename))

    # 如果返回的是 list of Future（tomorrow 行为），等它们
    # 兼容两种情况: 直接返回值 or list of futures
    if isinstance(futures, list):
        for f in futures:
            if hasattr(f, "result"):
                try:
                    f.result()
                except Exception as e:
                    print(f"线程异常: {e}")
    elif hasattr(futures, "result"):
        futures.result()

    print("=== 全部线程完成, 报告路径: {} ===".format(report_path))


if __name__ == "__main__":
    main()
