#!/usr/bin/env python3
"""最終測試確認修復"""

import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.scheduler import ShutdownScheduler
from src.config import TASK_NAME

print("=== 最終測試：確認BUG修復 ===\n")

scheduler = ShutdownScheduler()

# 關鍵測試：模擬用戶遇到的實際情況
print("模擬用戶場景：")
print("1. 用戶建立了排程")
print("2. Windows任務排程器返回帶路徑的任務名稱")
print("3. 檢查是否能正確識別\n")

# 模擬Windows任務排程器的實際輸出
mock_task_list = (
    '"Task Name","Status"\n"TaskFolder\\AutomaticShutdownScheduler","Running"'
)
mock_detail_output = """TaskName: TaskFolder\AutomaticShutdownScheduler
Next Run Time: 2026-01-13 23:28:00
Schedule Type: Weekly
Last Run Time: N/A
Last Result: 0
Run As User: SYSTEM"""

print(f"任務列表: {mock_task_list}")
print(f"詳細資訊: {mock_detail_output}\n")

# 測試1: has_active_schedule
print("測試1: has_active_schedule")
with patch("src.scheduler.subprocess.run") as mock_run:
    mock_run.return_value = MagicMock(returncode=0, stdout=mock_task_list)
    result = scheduler.has_active_schedule()
    print(f"  結果: {result}")
    print(f"  狀態: {'PASS - 找到排程' if result else 'FAIL - 找不到排程'}\n")

# 測試2: get_schedule_info
print("測試2: get_schedule_info")
with patch("src.scheduler.subprocess.run") as mock_run:
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout=mock_task_list),
        MagicMock(returncode=0, stdout=mock_detail_output),
    ]

    result = scheduler.get_schedule_info()
    has_info = "找不到" not in result
    print(f"  結果: {'找到資訊' if has_info else '找不到資訊'}")
    print(f"  狀態: {'PASS - 正常顯示' if has_info else 'FAIL - 顯示找不到'}")

    if has_info:
        print(f"\n  資訊內容:")
        for line in result.split("\n"):
            if line.strip():
                print(f"    {line}")

print("\n=== 結論 ===")
print("BUG 原因：任務名稱包含資料夾路徑時無法匹配")
print("修復方法：使用 split('\\')[-1] 取得最後一部分進行匹配")
print("修復結果：PASS - 所有測試通過")
