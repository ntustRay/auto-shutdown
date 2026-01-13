#!/usr/bin/env python3
"""
排程器模組的單元測試
測試 ShutdownScheduler 類別的所有核心功能
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sys

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler import ShutdownScheduler
from src.config import TASK_NAME, CONFIG_FILE_NAME


class TestShutdownScheduler(unittest.TestCase):
    """ShutdownScheduler 類別的測試"""

    def setUp(self):
        """測試前的設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.scheduler = ShutdownScheduler()
        self.scheduler.config_path = Path(self.temp_dir) / CONFIG_FILE_NAME

    def tearDown(self):
        """測試後的清理"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """測試初始化"""
        self.assertEqual(self.scheduler.task_name, TASK_NAME)
        self.assertEqual(self.scheduler.config_path.name, CONFIG_FILE_NAME)
        self.assertIn(TASK_NAME, self.scheduler.possible_task_names)
        self.assertIn("AutoShutdown", self.scheduler.possible_task_names)

    def test_save_and_load_config(self):
        """測試配置的保存和載入"""
        test_config = {
            "weekdays": [1, 2, 3],
            "time": "14:30",
            "is_repeat": True,
            "created_at": "2023-01-01T12:00:00",
        }

        # 測試保存
        self.scheduler._save_config(test_config)
        self.assertTrue(self.scheduler.config_path.exists())

        # 測試載入
        loaded_config = self.scheduler.load_config()
        self.assertEqual(loaded_config, test_config)

    def test_load_nonexistent_config(self):
        """測試載入不存在的配置"""
        result = self.scheduler.load_config()
        self.assertIsNone(result)

    @patch("src.scheduler.subprocess.run")
    def test_create_schedule_success(self, mock_run):
        """測試成功建立排程"""
        # 模擬成功的子程序執行
        mock_run.return_value = MagicMock(returncode=0)

        with patch.object(self.scheduler, "_save_config") as mock_save:
            self.scheduler.create_schedule([1, 2, 3], "14:30", True)

            # 驗證保存配置被調用
            mock_save.assert_called_once()

            # 驗證子程序被調用
            self.assertEqual(mock_run.call_count, 3)  # 刪除 + 創建 + 驗證

    @patch("src.scheduler.subprocess.run")
    def test_create_schedule_failure(self, mock_run):
        """測試建立排程失敗"""
        # 模擬失敗的子程序執行
        mock_run.return_value = MagicMock(returncode=1, stderr="Access denied")

        with self.assertRaises(RuntimeError) as context:
            self.scheduler.create_schedule([1, 2, 3], "14:30", True)

        self.assertIn("Task creation failed", str(context.exception))

    @patch("src.scheduler.subprocess.run")
    def test_remove_schedule_success(self, mock_run):
        """測試成功移除排程"""
        # 現在會調用兩次：shutdown /a 和 schtasks /delete
        mock_run.return_value = MagicMock(returncode=0)

        with patch.object(self.scheduler, "_save_config") as mock_save:
            self.scheduler.remove_schedule()

            # 驗證子程序被調用了兩次（shutdown /a + schtasks）
            self.assertEqual(mock_run.call_count, 2)

            # 驗證配置檔案被刪除
            self.assertFalse(self.scheduler.config_path.exists())

    @patch("src.scheduler.subprocess.run")
    def test_remove_schedule_config_file_error(self, mock_run):
        """測試移除排程時配置檔案刪除失敗"""
        mock_run.return_value = MagicMock(returncode=0)

        # 模擬配置檔案刪除失敗
        with patch("pathlib.Path.unlink", side_effect=OSError("Permission denied")):
            # 應該不拋出異常，只記錄警告
            self.scheduler.remove_schedule()

            # 驗證子程序仍然被調用了兩次
            self.assertEqual(mock_run.call_count, 2)

    @patch("src.scheduler.subprocess.run")
    def test_remove_schedule_aborts_shutdown(self, mock_run):
        """測試移除排程時會中止正在執行的關機命令"""
        # 模擬 shutdown /a 成功，然後 schtasks 刪除成功
        mock_run.side_effect = [
            MagicMock(returncode=0),  # shutdown /a 成功
            MagicMock(returncode=0),  # schtasks /delete 成功
        ]
        
        self.scheduler.remove_schedule()
        
        # 驗證 shutdown /a 被調用
        first_call = mock_run.call_args_list[0]
        self.assertEqual(first_call[0][0], ["shutdown", "/a"])
        
        # 驗證 schtasks 刪除也被調用
        second_call = mock_run.call_args_list[1]
        self.assertIn("schtasks", second_call[0][0])
        self.assertIn("/delete", second_call[0][0])

    @patch("src.scheduler.subprocess.run")
    def test_get_schedule_info_success(self, mock_run):
        """測試成功取得排程資訊"""
        # 模擬任務列表返回
        mock_run.side_effect = [
            MagicMock(
                returncode=0,
                stdout='"Task Name","Status"\n"AutomaticShutdownScheduler","Running"',
            ),
            MagicMock(
                returncode=0,
                stdout="Task Name: AutomaticShutdownScheduler\nNext Run Time: 2023-01-01 14:30:00",
            ),
        ]

        result = self.scheduler.get_schedule_info()

        self.assertIsInstance(result, str)
        self.assertIn("排程狀態", result)

    @patch("src.scheduler.subprocess.run")
    def test_get_schedule_info_no_task(self, mock_run):
        """測試沒有找到排程任務"""
        mock_run.return_value = MagicMock(
            returncode=0, stdout='"Task Name","Status"\n"OtherTask","Running"'
        )

        result = self.scheduler.get_schedule_info()
        self.assertEqual(result, "找不到排程任務")

    @patch("src.scheduler.subprocess.run")
    def test_has_active_schedule_true(self, mock_run):
        """測試檢查到活躍排程"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='"Task Name","Status"\n"AutomaticShutdownScheduler","Running"',
        )

        result = self.scheduler.has_active_schedule()
        self.assertTrue(result)

    @patch("src.scheduler.subprocess.run")
    def test_has_active_schedule_false(self, mock_run):
        """測試沒有活躍排程"""
        mock_run.return_value = MagicMock(
            returncode=0, stdout='"Task Name","Status"\n"OtherTask","Running"'
        )

        result = self.scheduler.has_active_schedule()
        self.assertFalse(result)

    @patch("src.scheduler.subprocess.run")
    def test_task_name_matching_fixed(self, mock_run):
        """測試任務名稱匹配邏輯已修復"""
        mock_run.return_value = MagicMock(
            returncode=0, stdout='"Task Name","Status"\n"AutomaticScheduler","Running"'
        )

        result = self.scheduler.has_active_schedule()
        # 這個任務名稱不應該被匹配，因為它不在 possible_task_names 中
        self.assertFalse(result)

    def test_time_validation(self):
        """測試時間格式驗證"""
        # 這裡可以添加時間格式驗證的測試
        # 由於時間驗證主要在 UI 層，這裡測試排程器是否接受正確格式
        try:
            # 這不會實際建立任務，但會驗證時間格式
            with patch("src.scheduler.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                self.scheduler.create_schedule([1], "23:59", True)
                # 如果沒有拋出異常，說明時間格式被接受
        except Exception as e:
            self.fail(f"Time validation failed: {e}")

    def test_weekdays_validation(self):
        """測試星期格式驗證"""
        # 測�试無效的星期格式
        with patch("src.scheduler.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            # 應該能處理各種有效的星期格式
            self.scheduler.create_schedule([1, 7], "12:00", True)  # 周一到周日

    @patch("src.scheduler.subprocess.run")
    def test_time_offset_for_warning(self, mock_run):
        """測試關機時間提前15分鐘的計算邏輯"""
        mock_run.return_value = MagicMock(returncode=0)
        
        # 測試案例：使用者設定 23:00 關機
        # 實際排程應該在 22:45 執行
        self.scheduler.create_schedule([1, 2, 3], "23:00", True)
        
        # 取得最後一次 create 命令的呼叫（第二次呼叫，第一次是 delete）
        create_call = None
        for call in mock_run.call_args_list:
            args = call[0][0]
            if "/create" in args:
                create_call = args
                break
        
        self.assertIsNotNone(create_call, "Should have called schtasks /create")
        
        # 驗證 /st 參數是 22:45 而不是 23:00
        st_index = create_call.index("/st")
        actual_time = create_call[st_index + 1]
        self.assertEqual(actual_time, "22:45", 
                        f"Expected task to run at 22:45 (15 min before 23:00), got {actual_time}")
    
    @patch("src.scheduler.subprocess.run")
    def test_time_offset_cross_midnight(self, mock_run):
        """測試跨越午夜的時間偏移計算"""
        mock_run.return_value = MagicMock(returncode=0)
        
        # 測試案例：使用者設定 00:10 關機
        # 實際排程應該在前一天的 23:55 執行
        self.scheduler.create_schedule([1], "00:10", True)
        
        # 取得 create 命令
        create_call = None
        for call in mock_run.call_args_list:
            args = call[0][0]
            if "/create" in args:
                create_call = args
                break
        
        st_index = create_call.index("/st")
        actual_time = create_call[st_index + 1]
        self.assertEqual(actual_time, "23:55",
                        f"Expected task to run at 23:55 (15 min before 00:10), got {actual_time}")


class TestSchedulerIntegration(unittest.TestCase):
    """排程器的集成測試"""

    def setUp(self):
        """測試前的設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.scheduler = ShutdownScheduler()
        self.scheduler.config_path = Path(self.temp_dir) / CONFIG_FILE_NAME

    def tearDown(self):
        """測試後的清理"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_lifecycle(self):
        """測試完整的建立-載入-移除生命週期"""
        test_config = {
            "weekdays": [1, 2, 3, 4, 5],
            "time": "18:00",
            "is_repeat": True,
            "created_at": "2023-01-01T12:00:00",
        }

        # 保存配置
        self.scheduler._save_config(test_config)
        self.assertTrue(self.scheduler.config_path.exists())

        # 載入配置
        loaded_config = self.scheduler.load_config()
        self.assertEqual(loaded_config, test_config)

        # 刪除配置
        self.scheduler.config_path.unlink()
        self.assertFalse(self.scheduler.config_path.exists())

        # 再次載入應該返回 None
        loaded_config = self.scheduler.load_config()
        self.assertIsNone(loaded_config)


if __name__ == "__main__":
    unittest.main()
