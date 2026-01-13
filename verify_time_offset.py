#!/usr/bin/env python3
"""驗證 15 分鐘時間偏移計算的簡單測試腳本"""

from datetime import datetime, timedelta

def test_time_offset():
    """測試不同時間的偏移計算"""
    
    test_cases = [
        ("23:00", "22:45"),  # 正常情況
        ("00:10", "23:55"),  # 跨越午夜
        ("14:30", "14:15"),  # 下午時間
        ("12:00", "11:45"),  # 中午
        ("00:00", "23:45"),  # 午夜
    ]
    
    print("測試 15 分鐘時間偏移計算")
    print("=" * 60)
    
    for user_time, expected_task_time in test_cases:
        hour, minute = map(int, user_time.split(":"))
        
        # 使用與 scheduler.py 相同的邏輯
        target_time = datetime(2000, 1, 1, hour, minute)
        actual_time = target_time - timedelta(minutes=15)
        actual_hour = actual_time.hour
        actual_minute = actual_time.minute
        calculated_time = f"{actual_hour:02d}:{actual_minute:02d}"
        
        status = "✓" if calculated_time == expected_task_time else "✗"
        print(f"{status} 使用者設定: {user_time} → 排程時間: {calculated_time} (預期: {expected_task_time})")
        
        if calculated_time != expected_task_time:
            print(f"  錯誤！預期 {expected_task_time}，但得到 {calculated_time}")
            return False
    
    print("=" * 60)
    print("所有測試通過！✓")
    return True

if __name__ == "__main__":
    success = test_time_offset()
    exit(0 if success else 1)
