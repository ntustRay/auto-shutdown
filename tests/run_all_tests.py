#!/usr/bin/env python3
"""
運行所有測試的腳本
提供統一的測試執行入口點
"""

import unittest
import sys
import os
import time
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """運行所有測試"""
    print("=" * 60)
    print("Auto Shutdown System - Test Suite")
    print("=" * 60)

    # 發現所有測試檔案
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob("test_*.py"))

    if not test_files:
        print("No test files found")
        return 1

    print(f"Found {len(test_files)} test files")

    # 創建測試套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_file in test_files:
        if test_file.name != "__init__.py":
            print(f"Loading test file: {test_file.name}")
            try:
                module = __import__(
                    f"tests.{test_file.stem}", fromlist=[test_file.stem]
                )
                tests = loader.loadTestsFromModule(module)
                suite.addTests(tests)
            except Exception as e:
                print(f"Failed to load test file {test_file.name}: {e}")
                return 1

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()

    # 輸出測試結果摘要
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    print(f"Total tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailed tests:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback}")

    if result.errors:
        print("\nError tests:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback}")

    # 輸出總體結果
    if result.wasSuccessful():
        print("\nAll tests passed!")
        return 0
    else:
        print(
            f"\nThere are {len(result.failures)} failed tests and {len(result.errors)} errors"
        )
        return 1


def run_specific_test(test_name):
    """運行特定的測試"""
    print(f"Running specific test: {test_name}")

    try:
        # 動態載入測試模組
        module = __import__(f"tests.{test_name}", fromlist=[test_name])
        suite = unittest.TestLoader().loadTestsFromModule(module)

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        if result.wasSuccessful():
            print("Test passed")
            return 0
        else:
            print("Test failed")
            return 1

    except ImportError:
        print(f"Test module not found: tests.{test_name}")
        return 1


def main():
    """主函數"""
    if len(sys.argv) > 1:
        # 運行特定測試
        test_name = sys.argv[1]
        return run_specific_test(test_name)
    else:
        # 運行所有測試
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())
