#!/usr/bin/env python3
"""
測試腳本，用於驗證所有修復是否正常工作
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """測試所有模組能否無錯誤匯入"""
    try:
        print("Testing imports...")
        
        # 測試配置匯入
        import src.config as config
        print("[OK] 配置匯入成功")
        
        # 測試排程器匯入
        from src.scheduler import ShutdownScheduler
        print("[OK] 排程器匯入成功")
        
        # 測試主題匯入
        from src.ui.modern_theme import COLORS, FONTS
        print("[OK] 主題匯入成功")
        
        # 測試元件匯入
        from src.ui.modern_widgets import ModernButton
        print("[OK] 元件匯入成功")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        traceback.print_exc()
        return False

def test_constants():
    """測試常數是否正確定義"""
    try:
        import src.config as config
        
        print("Testing constants...")
        assert config.WINDOW_WIDTH == 420
        assert config.WINDOW_HEIGHT == 750
        assert config.DEFAULT_HOUR == "23"
        assert "validation_error" in config.MESSAGES
        assert len(config.HELP_TIPS) == 3
        assert config.TASK_NAME == "AutomaticShutdownScheduler"
        
        print("[OK] All constants correct")
        return True
        
    except Exception as e:
        print(f"[FAIL] Constants test failed: {e}")
        return False

def test_scheduler_creation():
    """測試排程器能否無錯誤建立"""
    try:
        from src.scheduler import ShutdownScheduler
        
        print("Testing scheduler creation...")
        scheduler = ShutdownScheduler()
        assert scheduler.task_name == "AutomaticShutdownScheduler"
        assert scheduler.config_path.name == ".auto_shutdown_config.json"
        
        print("[OK] Scheduler creation successful")
        return True
        
    except Exception as e:
        print(f"[FAIL] Scheduler creation failed: {e}")
        return False

def main():
    """執行所有測試"""
    print("執行自動關機修復驗證測試...\n")
    
    tests = [
        test_imports,
        test_constants,
        test_scheduler_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All fixes verified successfully!")
        return 0
    else:
        print("Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
