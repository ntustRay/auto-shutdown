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
    """Get appropriate font family based on platform"""
    system = platform.system()
    
    if system == "Windows":
        # Windows font hierarchy
        return [
            "Microsoft JhengHei UI",
            "Microsoft JhengHei", 
            "Segoe UI",
            "Tahoma",
            "Arial",
            "sans-serif"
        ]
    elif system == "Darwin":  # macOS
        return [
            "PingFang SC",
            "Hiragino Sans GB",
            "Helvetica Neue",
            "Arial",
            "sans-serif"
        ]
    else:  # Linux and others
        return [
            "Noto Sans CJK SC",
            "WenQuanYi Micro Hei",
            "DejaVu Sans",
            "Arial",
            "sans-serif"
        ]

def get_safe_font(base_font_name, size, style="normal"):
    """Get font with fallback mechanism"""
    font_families = get_font_fallback()
    
    # Try the requested font first, then fallback
    for family in font_families:
        try:
            if family.lower() in base_font_name.lower():
                return (family, size, style)
        except (AttributeError, TypeError):
            continue
    
    # Use first available fallback
    return (font_families[0], size, style)

# Font definitions with fallback support
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
    """Configure ttk styles for modern look"""
    style = ttk.Style()

    # Use clam as base theme for better customization
    style.theme_use('clam')

    # Configure main frame
    style.configure(
        "Modern.TFrame",
        background=COLORS["surface_light"]
    )

    # Configure labels
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

    # Primary button style
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

    # Secondary button style
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
