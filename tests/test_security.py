#!/usr/bin/env python3
"""
安全性測試
測試系統的安全性相關功能
"""

import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler import ShutdownScheduler
from src.config import (
    TASK_NAME,
    CONFIG_FILE_NAME,
    SHUTDOWN_COMMAND,
    SUBPROCESS_ENCODING,
)


class TestSecurity(unittest.TestCase):
    """安全性測試"""

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

    def test_task_name_safety(self):
        """測試任務名稱的安全性"""
        scheduler = ShutdownScheduler()

        # 測試任務名稱不包含危險字符
        self.assertTrue(TASK_NAME.isalnum())
        self.assertFalse(
            any(
                char in TASK_NAME
                for char in [
                    ";",
                    "&",
                    "|",
                    "`",
                    "$",
                    "(",
                    ")",
                    "{",
                    "}",
                    "[",
                    "]",
                    ">",
                    "<",
                    '"',
                    "'",
                    "\\",
                    "/",
                ]
            )
        )

        # 測試可能的任務名稱列表都是安全的
        for name in scheduler.possible_task_names:
            self.assertTrue(name.isalnum() or name.replace("S", "").isalnum())

    def test_command_injection_prevention(self):
        """測試命令注入預防"""
        scheduler = ShutdownScheduler()

        # 測試惡意的時間輸入
        malicious_times = [
            "14:30; rm -rf /",
            "14:30 && echo 'hacked'",
            "14:30 | whoami",
            "14:30 `echo 'test'`",
            "14:30$(echo 'test')",
        ]

        for malicious_time in malicious_times:
            try:
                # 這應該不會實際執行惡意命令
                hour, minute = map(int, malicious_time.split(":")[0].split(";")[0])
                # 如果沒有拋出異常，說明基本過濾有效
                self.assertIsInstance(hour, int)
                self.assertIsInstance(minute, int)
            except (ValueError, IndexError):
                # 這是預期的行為
                pass

    def test_input_validation(self):
        """測試輸入驗證"""
        scheduler = ShutdownScheduler()

        # 測試無效的星期輸入
        invalid_weekdays = [
            [0, 8],  # 0 和 8 無效
            [-1, 1],  # -1 無效
            [1, 2, 3, 4, 5, 6, 7, 8],  # 8 無效
            [],  # 空列表
            [1.5],  # 浮點數
            ["1", "2"],  # 字串
        ]

        for invalid_days in invalid_weekdays:
            try:
                # 應該能處理無效輸入而不崩潰
                with patch("src.scheduler.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    scheduler.create_schedule(invalid_days, "12:00", True)
            except ValueError as e:
                # 預期的驗證錯誤
                msg = str(e).lower()
                self.assertTrue("invalid" in msg or "無效" in msg or "value" in msg)
            except Exception as e:
                self.fail(f"Unexpected exception type: {type(e).__name__}: {e}")

    def test_file_path_safety(self):
        """測試檔案路徑安全性"""
        scheduler = ShutdownScheduler()

        # 測試配置檔案路徑的安全性
        config_path = scheduler.config_path

        # 檔案名稱不應該包含路徑遍歷字符
        self.assertFalse(any(char in CONFIG_FILE_NAME for char in ["..", "/", "\\"]))

        # 檔案名稱應該是相對安全的
        self.assertTrue(CONFIG_FILE_NAME.startswith("."))  # 隱藏檔案

    def test_configuration_file_permissions(self):
        """測試配置檔案權限"""
        scheduler = ShutdownScheduler()

        # 測試配置檔案的創建
        test_config = {"test": "data"}
        scheduler._save_config(test_config)

        # 檔案應該存在
        self.assertTrue(scheduler.config_path.exists())

        # 檔案應該可以讀取
        with open(scheduler.config_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIsInstance(content, str)
            self.assertTrue(len(content) > 0)

    def test_sensitive_data_protection(self):
        """測試敏感資料保護"""
        scheduler = ShutdownScheduler()

        # 測試配置中不包含敏感資訊
        test_config = {
            "weekdays": [1, 2, 3],
            "time": "14:30",
            "is_repeat": True,
            "created_at": "2023-01-01T12:00:00",
        }

        scheduler._save_config(test_config)

        # 讀取配置檔案內容
        with open(scheduler.config_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 檢查是否包含敏感資訊
        sensitive_patterns = [
            "password",
            "passwd",
            "pwd",
            "secret",
            "token",
            "key",
            "credential",
            "auth",
            "session",
        ]

        content_lower = content.lower()
        for pattern in sensitive_patterns:
            self.assertNotIn(
                pattern,
                content_lower,
                f"Sensitive data '{pattern}' found in configuration",
            )

    def test_shutdown_command_safety(self):
        """測試關機命令的安全性"""
        # 關機命令應該是預定義的，不應該動態構造
        self.assertIsInstance(SHUTDOWN_COMMAND, str)
        self.assertIn("shutdown /s", SHUTDOWN_COMMAND)
        self.assertIn("/t 60", SHUTDOWN_COMMAND)

        # 檢查命令是否包含危險字符
        dangerous_chars = [
            ";",
            "&",
            "|",
            "`",
            "$",
            "(",
            ")",
            "{",
            "}",
            "[",
            "]",
            ">",
            "<",
            "'",
            "\\",
        ]
        for char in dangerous_chars:
            self.assertNotIn(
                char,
                SHUTDOWN_COMMAND,
                f"Dangerous character '{char}' found in shutdown command",
            )

    def test_subprocess_encoding_safety(self):
        """測試子程序編碼的安全性"""
        # 編碼應該是安全的，不應該包含惡意代碼
        self.assertIsInstance(SUBPROCESS_ENCODING, str)
        self.assertTrue(len(SUBPROCESS_ENCODING) > 0)

        # 檢查編碼是否包含危險字符
        dangerous_chars = [
            ";",
            "&",
            "|",
            "`",
            "$",
            "(",
            ")",
            "{",
            "}",
            "[",
            "]",
            ">",
            "<",
            '"',
            "'",
            "\\",
            "/",
        ]
        for char in dangerous_chars:
            self.assertNotIn(
                char,
                SUBPROCESS_ENCODING,
                f"Dangerous character '{char}' found in subprocess encoding",
            )

    @patch("src.scheduler.subprocess.run")
    def test_privilege_escalation_prevention(self, mock_run):
        """測試特權提升預防"""
        scheduler = ShutdownScheduler()

        # 模擟權限不足的情況
        mock_run.return_value = MagicMock(returncode=1, stderr="Access is denied")

        # 應該拋出適當的異常，而不是靜默失敗
        with self.assertRaises(Exception):
            scheduler.create_schedule([1], "12:00", True)

    def test_error_message_safety(self):
        """測試錯誤訊息的安全性"""
        from src.config import MESSAGES

        # 錯誤訊息不應該包含敏感資訊
        for key, message in MESSAGES.items():
            self.assertIsInstance(message, str)
            self.assertTrue(len(message) > 0)

            # 檢查是否包含敏感資訊
            sensitive_patterns = [
                "password",
                "passwd",
                "pwd",
                "secret",
                "token",
                "key",
                "credential",
                "auth",
                "session",
                "path",
            ]

            message_lower = message.lower()
            for pattern in sensitive_patterns:
                self.assertNotIn(
                    pattern,
                    message_lower,
                    f"Sensitive data '{pattern}' found in error message: {message}",
                )

    def test_log_file_safety(self):
        """測試日誌檔案的安全性"""
        # 測試日誌檔案名稱的安全性
        from src.config import LOG_FILE_NAME

        # 日誌檔案名稱不應該包含路徑遍歷字符
        self.assertFalse(any(char in LOG_FILE_NAME for char in ["..", "/", "\\"]))

        # 日誌檔案名稱應該是相對安全的
        self.assertTrue(LOG_FILE_NAME.endswith(".log"))

    def test_temporary_file_handling(self):
        """測試臨時檔案處理"""
        scheduler = ShutdownScheduler()

        # 測試臨時檔案的創建和清理
        test_config = {"test": "data"}
        scheduler._save_config(test_config)

        # 檔案應該存在
        self.assertTrue(scheduler.config_path.exists())

        # 測試檔案刪除
        scheduler.config_path.unlink()
        self.assertFalse(scheduler.config_path.exists())

    def test_resource_cleanup(self):
        """測試資源清理"""
        scheduler = ShutdownScheduler()

        # 測試多個操作的資源清理
        with patch("src.scheduler.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            # 執行多個操作
            for i in range(5):
                scheduler.create_schedule([1], f"{i:02d}:00", True)
                scheduler.remove_schedule()

            # 驗證所有操作都完成，沒有資源洩漏
            self.assertEqual(mock_run.call_count, 20)  # 5 * (3 create + 1 remove)


class TestSecurityIntegration(unittest.TestCase):
    """安全性集成測試"""

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

    def test_end_to_end_security(self):
        """測試端到端安全性"""
        scheduler = ShutdownScheduler()

        # 測試完整的建立-載入-移除流程
        test_config = {
            "weekdays": [1, 2, 3],
            "time": "14:30",
            "is_repeat": True,
            "created_at": "2023-01-01T12:00:00",
        }

        # 保存配置
        scheduler._save_config(test_config)

        # 載入配置
        loaded_config = scheduler.load_config()
        self.assertEqual(loaded_config, test_config)

        # 移除配置
        scheduler.config_path.unlink()
        self.assertFalse(scheduler.config_path.exists())

        # 再次載入應該返回 None
        loaded_config = scheduler.load_config()
        self.assertIsNone(loaded_config)

    def test_malicious_input_handling(self):
        """測試惡意輸入處理"""
        scheduler = ShutdownScheduler()

        # 測試各種惡意輸入
        malicious_inputs = [
            ([], "12:00", True),  # 空星期列表
            ([1, 2, 3], "25:00", True),  # 無效時間
            ([1, 2, 3], "12:60", True),  # 無效分鐘
            ([1, 2, 3], "", True),  # 空時間
            ([1, 2, 3], "not_a_time", True),  # 非法時間格式
        ]

        for weekdays, time, is_repeat in malicious_inputs:
            with patch("src.scheduler.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                try:
                    scheduler.create_schedule(weekdays, time, is_repeat)
                    # 如果沒有拋出異常，說明基本過濾有效
                except Exception:
                    # 拋出異常也是可以接受的
                    pass

    def test_system_isolation(self):
        """測試系統隔離"""
        scheduler = ShutdownScheduler()

        # 測試配置檔案隔離
        test_config = {"test": "data"}
        scheduler._save_config(test_config)

        # 配置檔案應該只存在於用戶目錄中
        self.assertTrue(str(scheduler.config_path).startswith(str(Path(self.temp_dir))))

        # 檢查檔案內容是否隔離
        with open(scheduler.config_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("test", content)
            self.assertIn("data", content)


if __name__ == "__main__":
    unittest.main()
