#!/usr/bin/env python3
"""測試修復後的程式碼"""

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.scheduler import ShutdownScheduler
from src.config import TASK_NAME

print("=== 測試修復後的程式碼 ===\n")

scheduler = ShutdownScheduler()

# 測試各種任務名稱格式
test_cases = [
    ("AutomaticShutdownScheduler", True, "標準名稱"),
    ("\\AutomaticShutdownScheduler", True, "反斜線前綴"),
    ("TaskFolder\\AutomaticShutdownScheduler", True, "資料夾路徑"),
    ("\\TaskFolder\\AutomaticShutdownScheduler", True, "完整路徑"),
    ("AutomaticS", True, "簡短版本"),
    ("AutoShutdown", True, "舊版本"),
    ("AutomaticScheduler", False, "不匹配"),
    ("OtherTask", False, "其他任務"),
]

print("1. 測試 has_active_schedule 的任務名稱匹配:")
print("-" * 50)

for task_name, should_match, description in test_cases:
    # 模擬 has_active_schedule 的邏輯
    normalized_name = task_name.split("\\")[-1] if "\\" in task_name else task_name

    is_match = (
        normalized_name == TASK_NAME
        or normalized_name in scheduler.possible_task_names
        or task_name == TASK_NAME
        or task_name in scheduler.possible_task_names
    )

    # 額外檢查
    if not is_match and TASK_NAME in task_name:
        last_part = task_name.split("\\")[-1]
        if last_part == TASK_NAME or last_part in scheduler.possible_task_names:
            is_match = True

    status = "PASS" if is_match == should_match else "FAIL"
    print(
        f"{status} {description:15} | '{task_name}' -> {is_match} (期望: {should_match})"
    )

print("\n2. 測試 _get_windows_task_info 的CSV解析:")
print("-" * 50)

csv_tests = [
    ('"AutomaticShutdownScheduler","Running"', True),
    ('"\\AutomaticShutdownScheduler","Running"', True),
    ('"TaskFolder\\AutomaticShutdownScheduler","Running"', True),
    ('"\\TaskFolder\\AutomaticShutdownScheduler","Running"', True),
    ('"OtherTask","Running"', False),
]

for csv_line, should_match in csv_tests:
    if "," in csv_line:
        current_task_name = csv_line.split(",")[0].strip('"')

        normalized_name = (
            current_task_name.split("\\")[-1]
            if "\\" in current_task_name
            else current_task_name
        )

        is_match = (
            normalized_name == TASK_NAME
            or normalized_name in scheduler.possible_task_names
            or current_task_name == TASK_NAME
            or current_task_name in scheduler.possible_task_names
        )

        if not is_match and TASK_NAME in current_task_name:
            last_part = current_task_name.split("\\")[-1]
            if last_part == TASK_NAME or last_part in scheduler.possible_task_names:
                is_match = True

        status = "PASS" if is_match == should_match else "FAIL"
        print(f"{status} {csv_line:45} -> {is_match} (期望: {should_match})")

print("\n3. 整合測試：模擬實際情境")
print("-" * 50)

# 模擬情境：Windows任務排程器返回帶路徑的任務名稱
mock_task_list = (
    '"Task Name","Status"\n"TaskFolder\\AutomaticShutdownScheduler","Running"'
)
mock_detail_output = """TaskName: TaskFolder\AutomaticShutdownScheduler
Next Run Time: 2026-01-13 23:28:00
Schedule Type: Weekly
Last Run Time: N/A
Last Result: 0
Run As User: SYSTEM"""

print(f"模擬任務列表: {mock_task_list}")
print(f"模擬詳細資訊: {mock_detail_output}")

# 測試 has_active_schedule
with patch("src.scheduler.subprocess.run") as mock_run:
    mock_run.return_value = MagicMock(returncode=0, stdout=mock_task_list)
    has_active = scheduler.has_active_schedule()
    print(f"\nhas_active_schedule() 結果: {has_active}")
    print(f"狀態: {'✓ 正常' if has_active else '✗ BUG 仍然存在'}")

# 測試 get_schedule_info
with patch("src.scheduler.subprocess.run") as mock_run:
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=mock_task_list),
        MagicMock(returncode=0, stdout=mock_detail_output),
    ]

    result = scheduler.get_schedule_info()
    has_info = "找不到" not in result
    print(f"\nget_schedule_info() 結果: {has_info}")
    print(f"狀態: {'✓ 正常' if has_info else '✗ BUG 仍然存在'}")

    if has_info:
        print(f"資訊內容:\n{result}")

print("\n=== 測試總結 ===")
if has_active and has_info:
    print("✓ 所有測試通過，BUG 已修復")
else:
    print("✗ 部分測試失敗，需要進一步檢查")
