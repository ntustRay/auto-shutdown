#!/usr/bin/env python3
"""
除蟲腳本 - 分析排程關機的BUG
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scheduler import ShutdownScheduler
from src.config import TASK_NAME


def test_bug_scenario():
    """測試用戶遇到的BUG場景"""
    print("=== 測試排程關機BUG ===\n")

    # 模擬一個場景：用戶已經建立了排程，但系統說找不到

    scheduler = ShutdownScheduler()

    # 測試1: 檢查has_active_schedule的邏輯
    print("測試1: has_active_schedule 方法")
    print("-" * 40)

    # 模擬Windows任務排程器返回的任務列表（包含我們的任務）
    mock_task_list = f'"Task Name","Status"\n"{TASK_NAME}","Running"'

    with patch("src.scheduler.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_task_list)

        result = scheduler.has_active_schedule()
        print(f"任務列表: {repr(mock_task_list)}")
        print(f"has_active_schedule() 返回: {result}")
        print(f"預期: True, 實際: {result}")
        print(f"測試1 {'通過' if result else '失敗'}\n")

    # 測試2: 檢查get_schedule_info的邏輯
    print("測試2: get_schedule_info 方法")
    print("-" * 40)

    # 模擬詳細任務資訊
    mock_detail_output = """TaskName: AutomaticShutdownScheduler
Next Run Time: 2026-01-13 23:28:00
Schedule Type: Weekly
Last Run Time: N/A
Last Result: 0
Run As User: SYSTEM"""

    with patch("src.scheduler.subprocess.run") as mock_run:
        # 第一次調用：列出任務
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=mock_task_list),  # 任務列表
            MagicMock(returncode=0, stdout=mock_detail_output),  # 詳細資訊
        ]

        result = scheduler.get_schedule_info()
        print(f"get_schedule_info() 返回: {repr(result)}")
        print(f"是否包含'找不到': {'找不到' in result}")
        print(f"測試2 {'通過' if '找不到' not in result else '失敗'}\n")

    # 測試3: 檢查UI的_check_schedule邏輯
    print("測試3: UI _check_schedule 邏輯")
    print("-" * 40)

    # 模擬get_schedule_info返回的格式化資訊
    formatted_info = """排程狀態：
任務名稱: AutomaticShutdownScheduler
下次執行時間: 2026-01-13 23:28:00
排程類型: Weekly
上次執行時間: N/A
上次執行結果: 0
執行身分: SYSTEM"""

    # 檢查條件
    task_info = formatted_info
    condition1 = bool(task_info)  # task_info 是否為真
    condition2 = "找不到" not in task_info  # 是否不包含"找不到"
    final_result = condition1 and condition2

    print(f"task_info: {repr(task_info)}")
    print(f"task_info 為真: {condition1}")
    print(f"不包含'找不到': {condition2}")
    print(f"最終結果: {final_result}")
    print(f"測試3 {'通過' if final_result else '失敗'}\n")

    # 測試4: 模擬任務名稱匹配的邊界情況
    print("測試4: 任務名稱匹配邊界情況")
    print("-" * 40)

    test_cases = [
        (TASK_NAME, True, "精確匹配"),
        ("\\AutomaticShutdownScheduler", True, "帶路徑前綴"),
        ("AutomaticS", True, "簡短版本"),
        ("AutoShutdown", True, "舊版本"),
        ("AutomaticScheduler", False, "不匹配"),
        ("OtherTask", False, "其他任務"),
    ]

    for task_name, should_match, description in test_cases:
        normalized_name = task_name.lstrip("\\")
        matches = (
            normalized_name == TASK_NAME
            or normalized_name in scheduler.possible_task_names
            or task_name == TASK_NAME
            or task_name in scheduler.possible_task_names
        )
        status = "PASS" if matches == should_match else "FAIL"
        print(
            f"{status} {description}: '{task_name}' -> {matches} (預期: {should_match})"
        )

    print("\n=== 測試完成 ===")


if __name__ == "__main__":
    test_bug_scenario()
