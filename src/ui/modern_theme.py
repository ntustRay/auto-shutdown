"""Modern theme colors and styling for the auto shutdown application"""
import tkinter as tk
from tkinter import ttk
import platform
import sys

# Color scheme matching the spec
COLORS = {
    # Primary colors
    "primary": "#6366f1",
    "primary_dark": "#4f46e5",
    "primary_light": "#818cf8",

    # Background colors
    "bg_light": "#f3f4f6",
    "bg_dark": "#111827",
    "surface_light": "#ffffff",
    "surface_dark": "#1f2937",

    # Text colors
    "text_main": "#1f2937",
    "text_sub": "#6b7280",
    "text_white": "#ffffff",

    # Status colors
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "inactive": "#9ca3af",

    # Border colors
    "border": "#e5e7eb",
    "border_dark": "#374151",
}

# Font fallback system for cross-platform compatibility
def get_font_fallback():
    """根據平台取得適當的字體系列"""
    system = platform.system()
    
    if system == "Windows":
        # Windows 字體層級
        return [
            "Microsoft JhengHei UI",
            "Microsoft JhengHei", 
            "Segoe UI",
            "Tahoma",
            "Arial",
            "sans-serif"
        ]
    elif system == "Darwin":  # macOS 系統
        return [
            "PingFang SC",
            "Hiragino Sans GB",
            "Helvetica Neue",
            "Arial",
            "sans-serif"
        ]
    else:  # Linux 和其他系統
        return [
            "Noto Sans CJK SC",
            "WenQuanYi Micro Hei",
            "DejaVu Sans",
            "Arial",
            "sans-serif"
        ]

def get_safe_font(base_font_name, size, style="normal"):
    """取得具有備用機制的字體"""
    font_families = get_font_fallback()
    
    # 先嘗試要求的字體，然後備用
    for family in font_families:
        try:
            if family.lower() in base_font_name.lower():
                return (family, size, style)
        except (AttributeError, TypeError):
            continue
    
    # 使用第一個可用的備用字體
    return (font_families[0], size, style)

# 具有備用支援的字體定義
FONTS = {
    "display_large": get_safe_font("Microsoft JhengHei UI Light", 52, "normal"),
    "display_medium": get_safe_font("Microsoft JhengHei UI Light", 36, "normal"),
    "title": get_safe_font("Microsoft JhengHei UI", 20, "bold"),
    "subtitle": get_safe_font("Microsoft JhengHei UI", 11, "normal"),
    "body": get_safe_font("Microsoft JhengHei UI", 10, "normal"),
    "button": get_safe_font("Microsoft JhengHei UI", 11, "bold"),
    "small": get_safe_font("Microsoft JhengHei UI", 9, "normal"),
    "tiny": get_safe_font("Microsoft JhengHei UI", 8, "normal"),
}


def configure_styles():
    """配置現代外觀的 ttk 樣式"""
    style = ttk.Style()

    # 使用 clam 作為基礎主題以獲得更好的自訂功能
    style.theme_use('clam')

    # 配置主框架
    style.configure(
        "Modern.TFrame",
        background=COLORS["surface_light"]
    )

    # 配置標籤
    style.configure(
        "Title.TLabel",
        background=COLORS["surface_light"],
        foreground=COLORS["text_main"],
        font=FONTS["title"]
    )

    style.configure(
        "Subtitle.TLabel",
        background=COLORS["surface_light"],
        foreground=COLORS["text_sub"],
        font=FONTS["subtitle"]
    )

    style.configure(
        "Body.TLabel",
        background=COLORS["surface_light"],
        foreground=COLORS["text_main"],
        font=FONTS["body"]
    )

    style.configure(
        "Small.TLabel",
        background=COLORS["surface_light"],
        foreground=COLORS["text_sub"],
        font=FONTS["small"]
    )

    # 主要按鈕樣式
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground=COLORS["text_white"],
        font=FONTS["button"],
        padding=(20, 12)
    )

    style.map(
        "Primary.TButton",
        background=[("active", COLORS["primary_dark"]), ("pressed", COLORS["primary_dark"])]
    )

    # 次要按鈕樣式
    style.configure(
        "Secondary.TButton",
        background=COLORS["bg_light"],
        foreground=COLORS["text_main"],
        font=FONTS["body"],
        padding=(15, 10)
    )

    style.map(
        "Secondary.TButton",
        background=[("active", COLORS["border"])]
    )

    return style
