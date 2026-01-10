"""UI module for auto shutdown application"""
from .main_window import AutoShutdownWindow
from .modern_theme import COLORS, FONTS, configure_styles
from .modern_widgets import (
    PillToggle, CircularDayButton, ModernToggle,
    ModernButton, CollapsibleSection, StatusIndicator
)

__all__ = [
    "AutoShutdownWindow",
    "COLORS",
    "FONTS",
    "configure_styles",
    "PillToggle",
    "CircularDayButton",
    "ModernToggle",
    "ModernButton",
    "CollapsibleSection",
    "StatusIndicator"
]