#!/usr/bin/env python3
"""
集成測試測試整個系統的協同工作
"""

import unittest
import tempfile
import shutil
import sys
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import tkinter

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler import ShutdownScheduler
from src.config import TASK_NAME, CONFIG_FILE_NAME, MESSAGES
from src.ui.main_window import AutoShutdownWindow


class TestSystemIntegration(unittest.TestCase):
    """系統集成測試"""

    def setUp(self):
        """測試前的設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = Path.home()

        # 模擬用戶目錄
        self.mock_home = Path(self.temp_dir)
        self.patcher = patch("pathlib.Path.home")
        self.mock_home_func = self.patcher.start()
        self.mock_home_func.return_value = self.mock_home

    def tearDown(self):
        """測試後的清理"""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scheduler_config_integration(self):
        """測試排程器和配置的集成"""
        scheduler = ShutdownScheduler()

        # 測試配置路徑是否正確
        self.assertEqual(scheduler.config_path.parent, self.mock_home)
        self.assertEqual(scheduler.config_path.name, CONFIG_FILE_NAME)

        # 測試配置保存和載入
        test_config = {
            "weekdays": [1, 2, 3, 4, 5],
            "time": "18:00",
            "is_repeat": True,
            "created_at": "2023-01-01T12:00:00",
        }

        scheduler._save_config(test_config)
        loaded_config = scheduler.load_config()
        self.assertEqual(loaded_config, test_config)

    def test_scheduler_task_name_matching(self):
        """測試排程器任務名稱匹配邏輯（修復後的測試）"""
        scheduler = ShutdownScheduler()

        # 測試可能的任務名稱列表
        expected_names = [TASK_NAME, "AutomaticS", "AutoShutdown"]

        self.assertEqual(scheduler.possible_task_names, expected_names)

        # 測試任務名稱匹配邏輯
        test_cases = [
            (TASK_NAME, True),  # 精確匹配
            ("AutomaticS", True),  # 簡短版本匹配
            ("AutoShutdown", True),  # 舊版本匹配
            ("AutomaticScheduler", False),  # 不應該匹配
            ("OtherTask", False),  # 不應該匹配
        ]

        for task_name, should_match in test_cases:
            # 模擬匹配邏輯
            matches = (
                task_name == TASK_NAME or task_name in scheduler.possible_task_names
            )
            self.assertEqual(
                matches, should_match, f"Task name '{task_name}' matching failed"
            )

    @patch("src.scheduler.subprocess.run")
    def test_full_scheduler_workflow(self, mock_run):
        """測試完整的排程器工作流程"""
        scheduler = ShutdownScheduler()

        # 模擬成功的子程序執行
        mock_run.return_value = MagicMock(returncode=0)

        # 測試建立排程
        scheduler.create_schedule([1, 2, 3], "14:30", True)

        # 驗證配置被保存
        self.assertTrue(scheduler.config_path.exists())

        # 測試載入配置
        config = scheduler.load_config()
        self.assertIsNotNone(config)
        self.assertEqual(config["weekdays"], [1, 2, 3])
        self.assertEqual(config["time"], "14:30")

        # 測試移除排程
        scheduler.remove_schedule()

        # 驗證配置被刪除
        self.assertFalse(scheduler.config_path.exists())

    def test_error_handling_integration(self):
        """測試錯誤處理的集成"""
        scheduler = ShutdownScheduler()

        # 測試配置載入失敗
        with patch("builtins.open", side_effect=FileNotFoundError):
            config = scheduler.load_config()
            self.assertIsNone(config)

        # 測試配置保存失敗
        with patch("builtins.open", side_effect=PermissionError):
            with self.assertRaises(Exception):
                scheduler._save_config({"test": "data"})

    def test_config_messages_consistency(self):
        """測試配置和訊息的一致性"""
        # 測試訊息常數的完整性
        self.assertIn("validation_error", MESSAGES)
        self.assertIn("permission_error", MESSAGES)
        self.assertIn("success_scheduled", MESSAGES)
        self.assertIn("success_canceled", MESSAGES)

        # 測試訊息內容的合理性
        self.assertTrue(len(MESSAGES["validation_error"]) > 0)
        self.assertTrue(len(MESSAGES["permission_error"]) > 0)
        self.assertTrue(len(MESSAGES["success_scheduled"]) > 0)
        self.assertTrue(len(MESSAGES["success_canceled"]) > 0)

    @patch("src.scheduler.subprocess.run")
    def test_scheduler_error_recovery(self, mock_run):
        """測試排程器的錯誤恢復機制"""
        scheduler = ShutdownScheduler()

        # 測試刪除現有任務時的錯誤處理
        mock_run.side_effect = [
            Exception("Access denied"),  # 刪除失敗
            MagicMock(returncode=0),  # 建立成功
            MagicMock(returncode=0),  # 驗證成功
        ]

        # 應該不拋出異常，而是記錄警告並繼續
        try:
            scheduler.create_schedule([1], "12:00", True)
            # 如果沒有拋出異常，說明錯誤恢復機制正常工作
        except Exception as e:
            self.fail(f"Scheduler should handle errors gracefully: {e}")

    def test_file_path_handling(self):
        """測試檔案路徑處理"""
        scheduler = ShutdownScheduler()

        # 測試配置路徑的正確性
        self.assertTrue(str(scheduler.config_path).endswith(CONFIG_FILE_NAME))

        # 測試路徑是 Path 物件
        self.assertIsInstance(scheduler.config_path, Path)

    @patch("src.scheduler.subprocess.run")
    def test_task_verification_workflow(self, mock_run):
        """測試任務驗證工作流程"""
        scheduler = ShutdownScheduler()

        # 模擬建立和驗證流程
        mock_run.side_effect = [
            MagicMock(returncode=1, stderr="Access denied"),  # 刪除現有任務失敗
            MagicMock(returncode=0),  # 建立新任務成功
            MagicMock(returncode=0),  # 驗證任務成功
        ]

        # 應該成功完成工作流程
        scheduler.create_schedule([1, 2], "13:00", True)

        # 驗證子程序被調用次數
        self.assertEqual(mock_run.call_count, 3)


class TestUIIntegration(unittest.TestCase):
    """UI 集成測試"""

    def setUp(self):
        """測試前的設定"""
        # 嘗試初始化 Tk，如果失敗（無顯示器）則 self.root 為 None
        try:
            self.root = tkinter.Tk()
            self.root.withdraw()
        except tkinter.TclError:
            self.root = None

    def tearDown(self):
        """測試後的清理"""
        if self.root:
            self.root.destroy()

    def test_ui_imports(self):
        """測試 UI 模組的匯入"""
        try:
            from src.ui.main_window import AutoShutdownWindow
            from src.ui.modern_theme import COLORS, FONTS
            from src.ui.modern_widgets import ModernButton

            # 如果沒有拋出異常，說明匯入成功
        except ImportError as e:
            self.fail(f"UI imports failed: {e}")

    def test_ui_component_creation(self):
        """測試 UI 元件的創建"""
        if self.root is None:
            self.skipTest("No display available")
            
        try:
            from src.ui.modern_widgets import ModernToggle, ModernButton

            # 模擬父元件
            mock_parent = MagicMock()

            # 測試創建各種元件
            toggle = ModernToggle(mock_parent)
            button = ModernButton(mock_parent, text="測試")

            self.assertIsNotNone(toggle)
            self.assertIsNotNone(button)

        except Exception as e:
            self.fail(f"UI component creation failed: {e}")

    def test_theme_application(self):
        """測試主題應用"""
        if self.root is None:
            self.skipTest("No display available")

        try:
            from src.ui.modern_theme import COLORS, FONTS, configure_styles

            # 測試色彩和字體定義
            self.assertIsInstance(COLORS, dict)
            self.assertIsInstance(FONTS, dict)

            # 測試樣式配置
            style = configure_styles()
            # style 可能是 None 或樣式物件
            if style is not None:
                self.assertTrue(hasattr(style, "configure"))

        except Exception as e:
            self.fail(f"Theme application failed: {e}")


class TestPerformanceIntegration(unittest.TestCase):
    """性能集成測試"""

    def setUp(self):
        """測試前的設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.patcher = patch("pathlib.Path.home")
        self.mock_home_func = self.patcher.start()
        self.mock_home_func.return_value = Path(self.temp_dir)

    def tearDown(self):
        """測試後的清理"""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scheduler_performance(self):
        """測試排程器性能"""
        import time

        scheduler = ShutdownScheduler()

        # 測試配置保存性能
        start_time = time.time()
        for i in range(100):
            scheduler._save_config({"test": f"data_{i}"})
        save_time = time.time() - start_time

        self.assertLess(save_time, 1.0, "Configuration saving too slow")

        # 測試配置載入性能
        start_time = time.time()
        for i in range(100):
            scheduler.load_config()
        load_time = time.time() - start_time

        self.assertLess(load_time, 1.0, "Configuration loading too slow")

    @patch("src.scheduler.subprocess.run")
    def test_concurrent_operations(self, mock_run):
        """測試並發操作"""
        scheduler = ShutdownScheduler()

        # 模擬快速連續操作
        mock_run.return_value = MagicMock(returncode=0)

        start_time = time.time()
        for i in range(10):
            scheduler.create_schedule([1], f"{i:02d}:00", True)
        operation_time = time.time() - start_time

        self.assertLess(operation_time, 5.0, "Concurrent operations too slow")


if __name__ == "__main__":
    unittest.main()
