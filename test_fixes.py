#!/usr/bin/env python3
"""
Test script to verify that all fixes work correctly
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        print("Testing imports...")
        
        # Test config import
        import src.config as config
        print("[OK] Config import successful")
        
        # Test scheduler import
        from src.scheduler import ShutdownScheduler
        print("[OK] Scheduler import successful")
        
        # Test theme import
        from src.ui.modern_theme import COLORS, FONTS
        print("[OK] Theme import successful")
        
        # Test widgets import
        from src.ui.modern_widgets import ModernButton
        print("[OK] Widgets import successful")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        traceback.print_exc()
        return False

def test_constants():
    """Test that constants are properly defined"""
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
    """Test that scheduler can be created without errors"""
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
    """Run all tests"""
    print("Running auto-shutdown fix verification tests...\n")
    
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
