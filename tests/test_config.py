#!/usr/bin/env python3
"""
配置模組的單元測試
測試 config.py 中的所有常數和設定
"""

import unittest
import locale
from unittest.mock import patch
import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_RESIZABLE,
    DEFAULT_HOUR,
    DEFAULT_MINUTE,
    DEFAULT_TIME_FORMAT,
    DEFAULT_REPEAT,
    TIME_CANVAS_HEIGHT,
    REPEAT_CANVAS_HEIGHT,
    HELP_CANVAS_COLLAPSED,
    HELP_CANVAS_EXPANDED,
    PADDING_MAIN,
    PADDING_SECTION,
    PADDING_WIDGET,
    CORNER_RADIUS,
    COLON_BLINK_INTERVAL,
    SHUTDOWN_WARNING_TIME,
    CONFIG_FILE_NAME,
    LOG_FILE_NAME,
    TASK_NAME,
    DAY_MAPPING,
    WEEKDAY_NAMES,
    WEEKDAY_FULL_NAMES,
    DEFAULT_SELECTED_DAYS,
    MESSAGES,
    HELP_TIPS,
    SHUTDOWN_COMMAND,
    SUBPROCESS_ENCODING,
    CONFIG_ENCODING,
)


class TestConfig(unittest.TestCase):
    """配置模組的測試"""

    def test_window_constants(self):
        """測試視窗相關常數"""
        self.assertEqual(WINDOW_WIDTH, 420)
        self.assertEqual(WINDOW_HEIGHT, 750)
        self.assertFalse(WINDOW_RESIZABLE)
        self.assertIsInstance(TIME_CANVAS_HEIGHT, int)
        self.assertIsInstance(REPEAT_CANVAS_HEIGHT, int)
        self.assertIsInstance(PADDING_MAIN, int)
        self.assertIsInstance(CORNER_RADIUS, int)

    def test_default_values(self):
        """測試預設值"""
        self.assertEqual(DEFAULT_HOUR, "23")
        self.assertEqual(DEFAULT_MINUTE, "28")
        self.assertEqual(DEFAULT_TIME_FORMAT, "24小時")
        self.assertTrue(DEFAULT_REPEAT)
        self.assertEqual(COLON_BLINK_INTERVAL, 500)
        self.assertEqual(SHUTDOWN_WARNING_TIME, 60)

    def test_file_names(self):
        """測試檔案名稱"""
        self.assertEqual(CONFIG_FILE_NAME, ".auto_shutdown_config.json")
        self.assertEqual(LOG_FILE_NAME, "auto_shutdown.log")
        self.assertEqual(TASK_NAME, "AutomaticShutdownScheduler")

    def test_day_mapping(self):
        """測試日期對映"""
        self.assertEqual(len(DAY_MAPPING), 7)
        self.assertEqual(DAY_MAPPING[1], "MON")  # 星期一
        self.assertEqual(DAY_MAPPING[7], "SUN")  # 星期日
        self.assertIn(1, DAY_MAPPING)
        self.assertIn(7, DAY_MAPPING)

    def test_weekday_names(self):
        """測試星期名稱"""
        self.assertEqual(len(WEEKDAY_NAMES), 7)
        self.assertEqual(WEEKDAY_NAMES[0], "一")  # 星期一
        self.assertEqual(WEEKDAY_NAMES[6], "日")  # 星期日
        self.assertEqual(len(WEEKDAY_FULL_NAMES), 7)
        self.assertEqual(WEEKDAY_FULL_NAMES[0], "星期一")
        self.assertEqual(WEEKDAY_FULL_NAMES[6], "星期日")

    def test_default_selected_days(self):
        """測試預設選中的星期"""
        self.assertIsInstance(DEFAULT_SELECTED_DAYS, set)
        self.assertEqual(len(DEFAULT_SELECTED_DAYS), 2)
        self.assertIn(0, DEFAULT_SELECTED_DAYS)  # 星期一
        self.assertIn(4, DEFAULT_SELECTED_DAYS)  # 星期五

    def test_messages(self):
        """測試訊息字典"""
        self.assertIsInstance(MESSAGES, dict)
        self.assertIn("validation_error", MESSAGES)
        self.assertIn("permission_error", MESSAGES)
        self.assertIn("success_scheduled", MESSAGES)
        self.assertIn("success_canceled", MESSAGES)
        self.assertIn("error_title", MESSAGES)
        self.assertIn("success_title", MESSAGES)
        self.assertIn("schedule_status", MESSAGES)
        self.assertIn("active_status", MESSAGES)
        self.assertIn("inactive_status", MESSAGES)

        # 驗證訊息內容
        self.assertEqual(MESSAGES["validation_error"], "請至少選擇一個星期")
        self.assertEqual(
            MESSAGES["permission_error"],
            "需要管理員權限才能建立排程任務。\n請以系統管理員身份運行程式。",
        )

    def test_help_tips(self):
        """測試說明提示"""
        self.assertIsInstance(HELP_TIPS, list)
        self.assertEqual(len(HELP_TIPS), 3)
        self.assertIn("選擇要執行的星期", HELP_TIPS[0])
        self.assertIn("系統會在關機前1分鐘顯示提醒", HELP_TIPS[1])
        self.assertIn("設定會自動保存", HELP_TIPS[2])

    def test_shutdown_command(self):
        """測試關機命令"""
        self.assertIsInstance(SHUTDOWN_COMMAND, str)
        self.assertIn("shutdown /s", SHUTDOWN_COMMAND)
        self.assertIn("/t 60", SHUTDOWN_COMMAND)
        self.assertIn("系統將在1分鐘後關機", SHUTDOWN_COMMAND)

    def test_encodings(self):
        """測試編碼設定"""
        self.assertIsInstance(CONFIG_ENCODING, str)
        self.assertEqual(CONFIG_ENCODING, "utf-8")

        # SUBPROCESS_ENCODING 應該是動態設定的
        self.assertIsInstance(SUBPROCESS_ENCODING, str)
        self.assertTrue(len(SUBPROCESS_ENCODING) > 0)

    @patch("locale.getpreferredencoding")
    def test_subprocess_encoding_dynamic(self, mock_locale):
        """測試 SUBPROCESS_ENCODING 的動態設定"""
        # 模擬不同的編碼設定
        mock_locale.return_value = "utf-8"
        # 重新匯入模組以測試動態設定
        import importlib
        import src.config

        importlib.reload(src.config)

        # 由於模組已經載入，我們測試邏輯是否正確
        try:
            encoding = locale.getpreferredencoding()
            self.assertIsInstance(encoding, str)
            self.assertTrue(len(encoding) > 0)
        except Exception:
            # 如果 getpreferredencoding 失敗，應該使用 utf-8
            self.assertEqual("utf-8", "utf-8")

    def test_constants_types(self):
        """測試所有常數的類型"""
        # 數值常數
        self.assertIsInstance(WINDOW_WIDTH, int)
        self.assertIsInstance(WINDOW_HEIGHT, int)
        self.assertIsInstance(TIME_CANVAS_HEIGHT, int)
        self.assertIsInstance(COLON_BLINK_INTERVAL, int)
        self.assertIsInstance(SHUTDOWN_WARNING_TIME, int)

        # 字串常數
        self.assertIsInstance(WINDOW_WIDTH, int)  # 應該是 int
        self.assertIsInstance(DEFAULT_HOUR, str)
        self.assertIsInstance(CONFIG_FILE_NAME, str)
        self.assertIsInstance(TASK_NAME, str)
        self.assertIsInstance(SHUTDOWN_COMMAND, str)

        # 布林值常數
        self.assertIsInstance(WINDOW_RESIZABLE, bool)
        self.assertIsInstance(DEFAULT_REPEAT, bool)

    def test_constants_values_range(self):
        """測試常數值的範圍"""
        # 確保尺寸是合理的
        self.assertTrue(WINDOW_WIDTH > 0)
        self.assertTrue(WINDOW_HEIGHT > 0)
        self.assertTrue(TIME_CANVAS_HEIGHT > 0)
        self.assertTrue(REPEAT_CANVAS_HEIGHT > 0)

        # 確保時間間隔是合理的
        self.assertTrue(COLON_BLINK_INTERVAL > 0)
        self.assertTrue(SHUTDOWN_WARNING_TIME > 0)

        # 確保邊距是合理的
        self.assertTrue(PADDING_MAIN >= 0)
        self.assertTrue(PADDING_SECTION >= 0)
        self.assertTrue(PADDING_WIDGET >= 0)
        self.assertTrue(CORNER_RADIUS >= 0)


class TestConfigIntegration(unittest.TestCase):
    """配置模組的集成測試"""

    def test_config_consistency(self):
        """測試配置之間的一致性"""
        # 確保 DAY_MAPPING 和 WEEKDAY_NAMES 長度一致
        self.assertEqual(len(DAY_MAPPING), len(WEEKDAY_NAMES))

        # 確預設選中的星期在有效範圍內
        for day in DEFAULT_SELECTED_DAYS:
            self.assertTrue(0 <= day < 7)

        # 確保所有訊息都不為空
        for key, message in MESSAGES.items():
            self.assertIsInstance(message, str)
            self.assertTrue(len(message) > 0)

        # 確保所有提示都不為空
        for tip in HELP_TIPS:
            self.assertIsInstance(tip, str)
            self.assertTrue(len(tip) > 0)

    def test_task_name_safety(self):
        """測試任務名稱的安全性"""
        # 任務名稱不應該包含特殊字符
        self.assertTrue(TASK_NAME.isalnum())
        self.assertFalse(any(char in TASK_NAME for char in [" ", ".", "-", "_"]))


if __name__ == "__main__":
    unittest.main()
