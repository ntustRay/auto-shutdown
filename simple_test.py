#!/usr/bin/env python3
"""簡單除蟲測試"""

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.scheduler import ShutdownScheduler
from src.config import TASK_NAME

print("=== 排程關機BUG分析 ===\n")

# 測試關鍵問題：get_schedule_info 在任務存在時返回什麼？
scheduler = ShutdownScheduler()

# 模擬任務列表包含我們的任務
task_list_csv = f'"Task Name","Status"\n"{TASK_NAME}","Running"'
detail_output = """TaskName: AutomaticShutdownScheduler
Next Run Time: 2026-01-13 23:28:00
Schedule Type: Weekly
Last Run Time: N/A
Last Result: 0
Run As User: SYSTEM"""

print("1. 模擬get_schedule_info的執行流程:")
with patch("src.scheduler.subprocess.run") as mock_run:
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=task_list_csv),  # 列出任務
        MagicMock(returncode=0, stdout=detail_output),  # 取得詳細資訊
    ]

    result = scheduler.get_schedule_info()
    print(f"   返回結果類型: {type(result)}")
    print(f"   返回結果內容: {repr(result)}")
    print(f"   是否包含'找不到': {'找不到' in result}")
    print(f"   結果為空: {not result}")
    print()

# 測試UI的檢查邏輯
print("2. UI檢查邏輯:")
task_info = result  # get_schedule_info的返回值
condition1 = bool(task_info)  # task_info 是否為真
condition2 = "找不到" not in str(task_info)  # 是否不包含"找不到"
final_result = condition1 and condition2

print(f"   task_info = {repr(task_info)}")
print(f"   task_info 為真: {condition1}")
print(f"   不包含'找不到': {condition2}")
print(f"   最終判斷結果: {final_result}")
print()

# 測試has_active_schedule
print("3. has_active_schedule 測試:")
with patch("src.scheduler.subprocess.run") as mock_run:
    mock_run.return_value = MagicMock(returncode=0, stdout=task_list_csv)
    has_active = scheduler.has_active_schedule()
    print(f"   has_active_schedule(): {has_active}")
    print()

print("=== 結論 ===")
if final_result and has_active:
    print("✓ 理論上一切正常")
else:
    print("✗ 發現問題:")
    if not final_result:
        print(f"  - UI檢查失敗: task_info={repr(task_info)}")
    if not has_active:
        print(f"  - has_active_schedule 失敗")
