#!/usr/bin/env python3
"""測試立即關機邏輯"""

from datetime import datetime, timedelta

def test_immediate_shutdown_logic():
    """測試在 15 分鐘內設定關機時間的邏輯"""
    
    SHUTDOWN_WARNING_TIME = 900  # 15 minutes
    
    print("測試立即關機邏輯")
    print("=" * 60)
    
    test_cases = [
        # (current_time, target_time, should_execute_immediately)
        ("01:43", "01:50", True),   # 7 分鐘內
        ("01:43", "01:58", True),   # 15 分鐘內
        ("01:43", "01:59", False),  # 16 分鐘後
        ("01:43", "02:00", False),  # 17 分鐘後
        ("23:50", "23:55", True),   # 5 分鐘內
        ("23:50", "00:04", True),   # 跨午夜 14 分鐘
        ("23:50", "00:06", False),  # 跨午夜 16 分鐘
    ]
    
    for current_str, target_str, should_immediate in test_cases:
        # 模擬當前時間
        now_h, now_m = map(int, current_str.split(":"))
        target_h, target_m = map(int, target_str.split(":"))
        
        # 使用今天的時間
        now = datetime.now().replace(hour=now_h, minute=now_m, second=0, microsecond=0)
        today_target_time = now.replace(hour=target_h, minute=target_m, second=0, microsecond=0)
        
        # 如果目標時間已過，嘗試明天
        if today_target_time < now:
            today_target_time += timedelta(days=1)
        
        time_until_shutdown = (today_target_time - now).total_seconds()
        will_execute_immediately = time_until_shutdown <= SHUTDOWN_WARNING_TIME
        
        status = "✓" if will_execute_immediately == should_immediate else "✗"
        action = "立即執行" if will_execute_immediately else "建立排程"
        
        print(f"{status} 現在 {current_str}, 設定 {target_str} 關機")
        print(f"   → 距離關機還有 {int(time_until_shutdown//60)} 分鐘")
        print(f"   → 動作: {action}")
        
        if will_execute_immediately != should_immediate:
            print(f"   錯誤！預期應該 {'立即執行' if should_immediate else '建立排程'}")
            return False
    
    print("=" * 60)
    print("所有測試通過！✓")
    return True

if __name__ == "__main__":
    success = test_immediate_shutdown_logic()
    exit(0 if success else 1)
