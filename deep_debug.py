#!/usr/bin/env python3
"""深入除蟲 - 檢查任務名稱匹配問題"""

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.scheduler import ShutdownScheduler
from src.config import TASK_NAME

print("=== 深入除蟲：任務名稱匹配問題 ===\n")

scheduler = ShutdownScheduler()

# 測試各種可能的任務名稱格式
test_cases = [
    # (任務名稱, 是否應該匹配, 描述)
    ("AutomaticShutdownScheduler", True, "標準名稱"),
    ("\\AutomaticShutdownScheduler", True, "帶反斜線前綴"),
    ("/AutomaticShutdownScheduler", True, "帶正斜線前綴"),
    ("TaskFolder\\AutomaticShutdownScheduler", True, "帶資料夾路徑"),
    ("\\TaskFolder\\AutomaticShutdownScheduler", True, "帶完整路徑"),
    ("AutomaticS", True, "簡短版本"),
    ("AutoShutdown", True, "舊版本"),
    ("AutomaticScheduler", False, "不匹配"),
    ("OtherTask", False, "其他任務"),
    ("AutomaticShutdownScheduler ", False, "尾部空格"),
    (" AutomaticShutdownScheduler", False, "開頭空格"),
]

print("任務名稱匹配測試:")
print("-" * 60)

for task_name, should_match, description in test_cases:
    # 模擬has_active_schedule的邏輯
    normalized_name = task_name.lstrip("\\")

    matches = (
        normalized_name == TASK_NAME
        or normalized_name in scheduler.possible_task_names
        or task_name == TASK_NAME
        or task_name in scheduler.possible_task_names
    )

    status = "PASS" if matches == should_match else "FAIL"
    print(
        f"{status} {description:20} | '{task_name}' -> {matches} (期望: {should_match})"
    )

print("\n=== 檢查 _get_windows_task_info 的問題 ===\n")

# 測試 _get_windows_task_info 的CSV解析
print("CSV格式解析測試:")
csv_lines = [
    '"Task Name","Status"',
    '"AutomaticShutdownScheduler","Running"',
    '"\\AutomaticShutdownScheduler","Running"',
    '"TaskFolder\\AutomaticShutdownScheduler","Running"',
    '"OtherTask","Running"',
]

for line in csv_lines:
    if "," in line:
        current_task_name = line.split(",")[0].strip('"')
        normalized_name = current_task_name.lstrip("\\")

        matches = (
            normalized_name == TASK_NAME
            or normalized_name in scheduler.possible_task_names
            or current_task_name == TASK_NAME
            or current_task_name in scheduler.possible_task_names
        )

        print(f"  CSV: {line:45} -> 提取: '{current_task_name}' -> 匹配: {matches}")

print("\n=== 可能的BUG原因 ===")
print("1. 任務名稱包含特殊字符或路徑")
print("2. CSV解析時的引號處理問題")
print("3. 編碼問題導致的任務名稱識別錯誤")
print("4. Windows系統語言導致的任務名稱翻譯問題")
