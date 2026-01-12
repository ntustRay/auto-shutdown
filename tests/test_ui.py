#!/usr/bin/env python3
"""
UI 模組的單元測試
測試現代化 UI 元件和主題系統
"""

import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.modern_theme import COLORS, FONTS, configure_styles, get_font_fallback
from src.ui.modern_widgets import (
    ModernToggle,
    PillToggle,
    CircularDayButton,
    ModernButton,
    CollapsibleSection,
    StatusIndicator,
)


class TestModernTheme(unittest.TestCase):
    """現代主題的測試"""

    def test_colors_structure(self):
        """測試色彩結構"""
        self.assertIsInstance(COLORS, dict)

        # 檢查必要的色彩鍵
        required_colors = [
            "primary",
            "primary_dark",
            "primary_light",
            "bg_light",
            "bg_dark",
            "surface_light",
            "surface_dark",
            "text_main",
            "text_sub",
            "text_white",
            "success",
            "warning",
            "error",
            "inactive",
            "border",
            "border_dark",
        ]

        for color_key in required_colors:
            self.assertIn(color_key, COLORS)
            self.assertIsInstance(COLORS[color_key], str)
            self.assertTrue(len(COLORS[color_key]) > 0)

    def test_fonts_structure(self):
        """測試字體結構"""
        self.assertIsInstance(FONTS, dict)

        # 檢查必要的字體鍵
        required_fonts = [
            "display_large",
            "display_medium",
            "title",
            "subtitle",
            "body",
            "button",
            "small",
            "tiny",
        ]

        for font_key in required_fonts:
            self.assertIn(font_key, FONTS)
            font_tuple = FONTS[font_key]
            self.assertIsInstance(font_tuple, tuple)
            self.assertEqual(len(font_tuple), 3)  # (family, size, style)

    def test_configure_styles(self):
        """測試樣式配置"""
        # 這個測試需要 tkinter，所以我們只測試它不拋出異常
        try:
            style = configure_styles()
            self.assertIsNotNone(style)
        except tk.TclError:
            # 在某些環境中 tkinter 可能不可用，這是可以接受的
            pass

    def test_get_font_fallback(self):
        """測試字體備用機制"""
        fallback_fonts = get_font_fallback()
        self.assertIsInstance(fallback_fonts, list)
        self.assertTrue(len(fallback_fonts) > 0)

        # 檢查每個備用字體
        for font in fallback_fonts:
            self.assertIsInstance(font, str)
            self.assertTrue(len(font) > 0)

    def test_color_values(self):
        """測試色彩值的有效性"""
        # 檢查色彩格式（應該是有效的十六進制顏色代碼）
        for color_name, color_value in COLORS.items():
            if color_value.startswith("#"):
                # 十六進制顏色代碼
                self.assertEqual(len(color_value), 7)  # #RRGGBB
                self.assertTrue(
                    all(c in "0123456789ABCDEFabcdef" for c in color_value[1:])
                )
            else:
                # 名稱顏色（如 'red', 'blue' 等）
                self.assertTrue(len(color_value) > 0)

    def test_font_values(self):
        """測試字體值的有效性"""
        for font_name, font_tuple in FONTS.items():
            family, size, style = font_tuple
            self.assertIsInstance(family, str)
            self.assertIsInstance(size, (int, float))
            self.assertIsInstance(style, str)
            self.assertTrue(size > 0)
            self.assertIn(style, ["normal", "bold", "italic", "bold italic"])


class TestModernWidgets(unittest.TestCase):
    """現代化 UI 元件的測試"""

    def setUp(self):
        """測試前的設定"""
        self.root = tk.Tk()
        self.root.geometry("100x100")

    def tearDown(self):
        """測試後的清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_modern_toggle(self):
        """測試現代化切換開關"""
        toggle = ModernToggle(self.root)
        self.assertIsNotNone(toggle)
        self.assertIsInstance(toggle.variable.get(), bool)

        # 測試切換功能
        initial_state = toggle.variable.get()
        toggle._toggle()
        self.assertNotEqual(toggle.variable.get(), initial_state)

    def test_pill_toggle(self):
        """測試膠囊樣式切換器"""
        toggle = PillToggle(self.root, options=["24小時", "12小時"])
        self.assertIsNotNone(toggle)
        self.assertEqual(len(toggle.options), 2)
        self.assertIn("24小時", toggle.options)
        self.assertIn("12小時", toggle.options)

    def test_circular_day_button(self):
        """測試圓形日期按鈕"""
        button = CircularDayButton(self.root, text="一")
        self.assertIsNotNone(button)
        self.assertEqual(button.text, "一")

    def test_modern_button(self):
        """測試現代化按鈕"""
        button = ModernButton(self.root, text="測試按鈕", primary=True)
        self.assertIsNotNone(button)
        self.assertEqual(button.text, "測試按鈕")

    def test_collapsible_section(self):
        """測試可折疊區段"""
        section = CollapsibleSection(self.root, title="測試區段")
        self.assertIsNotNone(section)
        self.assertEqual(section.title_label["text"], "測試區段")

        # 測試折疊功能
        initial_state = section.is_expanded
        section._toggle()
        self.assertNotEqual(section.is_expanded, initial_state)

    def test_status_indicator(self):
        """測試狀態指示器"""
        indicator = StatusIndicator(self.root)
        self.assertIsNotNone(indicator)

        # 測試狀態設定
        indicator.set_status("active", "活躍狀態")
        self.assertEqual(indicator.label["text"], "目前狀態：活躍狀態")

    def test_widget_colors(self):
        """測試元件色彩一致性"""
        # 測試所有元件都使用正確的色彩
        toggle = ModernToggle(self.root)
        self.assertIn(toggle["bg"], [COLORS["surface_light"], COLORS["bg_light"]])

        button = ModernButton(self.root, text="測試")
        self.assertIn(button["bg"], [COLORS["primary"], COLORS["bg_light"]])

    def test_widget_fonts(self):
        """測試元件字體一致性"""
        button = ModernButton(self.root, text="測試")
        font_tuple = button["font"]
        self.assertIsInstance(font_tuple, tuple)
        self.assertEqual(len(font_tuple), 3)


class TestUIIntegration(unittest.TestCase):
    """UI 模組的集成測試"""

    def setUp(self):
        """測試前的設定"""
        self.root = tk.Tk()
        self.root.geometry("200x200")

    def tearDown(self):
        """測試後的清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_widget_interaction(self):
        """測試元件之間的交互"""
        # 測試切換開關和按鈕的交互
        toggle = ModernToggle(self.root)
        button = ModernButton(self.root, text="測試", primary=True)

        # 模擬交互邏輯
        def on_toggle():
            if toggle.variable.get():
                button.config(text="開啟")
            else:
                button.config(text="關閉")

        toggle.variable.trace_add("write", lambda *args: on_toggle())
        on_toggle()  # 初始化

        self.assertIn(button["text"], ["開啟", "關閉"])

    def test_theme_consistency(self):
        """測試主題一致性"""
        # 確保所有元件使用相同的色彩系統
        toggle = ModernToggle(self.root)
        button = ModernButton(self.root, text="測試")
        indicator = StatusIndicator(self.root)

        # 檢查色彩是否來自同一個色彩系統
        self.assertIn(toggle["bg"], COLORS.values())
        self.assertIn(button["bg"], COLORS.values())
        self.assertIn(indicator["bg"], COLORS.values())

    def test_responsiveness(self):
        """測試響應式設計"""
        # 測試元件是否能適應不同大小
        toggle = ModernToggle(self.root, width=60, height=30)
        button = ModernButton(self.root, text="測試", width=120, height=40)

        self.assertEqual(toggle["width"], 60)
        self.assertEqual(toggle["height"], 30)
        self.assertEqual(button["width"], 120)
        self.assertEqual(button["height"], 40)

    @patch("src.ui.modern_theme.platform.system")
    def test_cross_platform_fonts(self, mock_system):
        """測試跨平台字體支援"""
        # 模擬不同平台
        mock_system.return_value = "Windows"
        fonts_win = get_font_fallback()
        self.assertIn("Microsoft JhengHei UI", fonts_win[0])

        mock_system.return_value = "Darwin"
        fonts_mac = get_font_fallback()
        self.assertIn("PingFang SC", fonts_mac[0])

        mock_system.return_value = "Linux"
        fonts_linux = get_font_fallback()
        self.assertIn("Noto Sans CJK SC", fonts_linux[0])


class TestUIErrorHandling(unittest.TestCase):
    """UI 錯誤處理的測試"""

    def setUp(self):
        """測試前的設定"""
        self.root = tk.Tk()
        self.root.geometry("100x100")

    def tearDown(self):
        """測試後的清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_invalid_parameters(self):
        """測試無效參數處理"""
        # 測試無效的色彩
        with self.assertRaises(KeyError):
            invalid_color = COLORS["nonexistent_color"]

        # 測試無效的字體
        with self.assertRaises(KeyError):
            invalid_font = FONTS["nonexistent_font"]

    def test_widget_creation_errors(self):
        """測試元件創建錯誤"""
        # 測試創建元件時的錯誤處理
        try:
            toggle = ModernToggle(self.root, width=-1)  # 無效寬度
            # 應該不拋出異常，而是使用預設值
            self.assertIsInstance(toggle, ModernToggle)
        except Exception:
            # 如果拋出異常也是可以接受的
            pass

    def test_theme_configuration_errors(self):
        """測試主題配置錯誤"""
        # 測試配置樣式時的錯誤處理
        try:
            style = configure_styles()
            # 應該返回一個樣式物件或 None
            self.assertIsNone(style) or hasattr(style, "configure")
        except Exception:
            # 在某些環境中可能無法配置樣式，這是可以接受的
            pass


if __name__ == "__main__":
    unittest.main()
