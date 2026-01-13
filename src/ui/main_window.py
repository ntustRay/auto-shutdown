"""Modern main window for the auto shutdown application"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from ..scheduler import ShutdownScheduler
from .modern_theme import COLORS, FONTS, configure_styles
from .modern_widgets import (
    PillToggle,
    CircularDayButton,
    ModernToggle,
    ModernButton,
    CollapsibleSection,
    StatusIndicator,
)
from ..config import (
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
    WEEKDAY_NAMES,
    WEEKDAY_FULL_NAMES,
    DEFAULT_SELECTED_DAYS,
    MESSAGES,
    HELP_TIPS,
    BUTTON_HEIGHT_LARGE,
    BUTTON_HEIGHT_MEDIUM,
)
import logging

logger = logging.getLogger(__name__)


class AutoShutdownWindow:
    """Modern application window for auto shutdown scheduling"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("自動關機系統")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(WINDOW_RESIZABLE, WINDOW_RESIZABLE)
        self.root.configure(bg=COLORS["bg_light"])

        # Configure styles
        configure_styles()

        self.scheduler = ShutdownScheduler()
        self.weekday_vars = []

        # Time variables using config defaults
        self.hour_var = tk.StringVar(value=DEFAULT_HOUR)
        self.minute_var = tk.StringVar(value=DEFAULT_MINUTE)
        self.time_format_var = tk.StringVar(value=DEFAULT_TIME_FORMAT)
        self.repeat_var = tk.BooleanVar(value=DEFAULT_REPEAT)

        # Animation state
        self.colon_visible = True

        self._create_ui()
        self._load_saved_config()
        self._start_colon_animation()

    def _create_ui(self):
        """Create the modern user interface"""
        # Main container
        self.main_container = tk.Frame(self.root, bg=COLORS["surface_light"])
        self.main_container.pack(
            fill="both", expand=True, padx=PADDING_MAIN, pady=PADDING_MAIN
        )

        # Header section
        self._create_header()

        # Time section
        self._create_time_section()

        # Weekday section
        self._create_weekday_section()

        # Repeat toggle section
        self._create_repeat_section()

        # Help section
        self._create_help_section()

        # Status indicator
        self._create_status_section()

        # Action buttons
        self._create_action_buttons()

    def _create_header(self):
        """Create header with title and subtitle"""
        header_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        header_frame.pack(fill="x", pady=(PADDING_WIDGET // 2, PADDING_SECTION))

        title = tk.Label(
            header_frame,
            text="自動關機系統",
            font=FONTS["title"],
            fg=COLORS["text_main"],
            bg=COLORS["surface_light"],
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header_frame,
            text="智慧排程管理您的設備",
            font=FONTS["subtitle"],
            fg=COLORS["text_sub"],
            bg=COLORS["surface_light"],
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _create_time_section(self):
        """Create the time display and format toggle"""
        # Outer container for rounded effect
        outer_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        outer_frame.pack(fill="x", pady=(0, PADDING_SECTION))

        # Create rounded container using canvas
        time_canvas = tk.Canvas(
            outer_frame,
            bg=COLORS["surface_light"],
            highlightthickness=0,
            height=TIME_CANVAS_HEIGHT,
        )
        time_canvas.pack(fill="x")

        # Draw rounded rectangle background
        def draw_rounded_bg(event=None):
            time_canvas.delete("bg")
            w = time_canvas.winfo_width()
            h = 200
            r = 16
            # Draw rounded rectangle
            time_canvas.create_arc(
                0,
                0,
                2 * r,
                2 * r,
                start=90,
                extent=90,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            time_canvas.create_arc(
                w - 2 * r,
                0,
                w,
                2 * r,
                start=0,
                extent=90,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            time_canvas.create_arc(
                0,
                h - 2 * r,
                2 * r,
                h,
                start=180,
                extent=90,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            time_canvas.create_arc(
                w - 2 * r,
                h - 2 * r,
                w,
                h,
                start=270,
                extent=90,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            time_canvas.create_rectangle(
                r,
                0,
                w - r,
                h,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            time_canvas.create_rectangle(
                0,
                r,
                w,
                h - r,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            # Top accent line
            time_canvas.create_rectangle(
                0, 0, w, 3, fill=COLORS["primary"], outline=COLORS["primary"], tags="bg"
            )
            time_canvas.tag_lower("bg")

        time_canvas.bind("<Configure>", draw_rounded_bg)

        # Inner frame for content
        inner_frame = tk.Frame(time_canvas, bg=COLORS["bg_light"])
        inner_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Time format toggle (centered)
        toggle_container = tk.Frame(inner_frame, bg=COLORS["bg_light"])
        toggle_container.pack(pady=(0, 16))

        self.format_toggle = PillToggle(
            toggle_container,
            options=["24小時", "12小時"],
            variable=self.time_format_var,
            command=self._on_format_change,
            button_width=55,
            button_height=26,
        )
        self.format_toggle.pack()

        # Large time display
        time_display_frame = tk.Frame(inner_frame, bg=COLORS["bg_light"])
        time_display_frame.pack()

        # Hour
        self.hour_label = tk.Label(
            time_display_frame,
            textvariable=self.hour_var,
            font=FONTS["display_large"],
            fg=COLORS["primary"],
            bg=COLORS["bg_light"],
            cursor="hand2",
        )
        self.hour_label.pack(side="left")
        self.hour_label.bind("<Button-1>", self._show_hour_picker)

        # Colon
        self.colon_label = tk.Label(
            time_display_frame,
            text=":",
            font=FONTS["display_large"],
            fg=COLORS["text_main"],
            bg=COLORS["bg_light"],
        )
        self.colon_label.pack(side="left")

        # Minute
        self.minute_label = tk.Label(
            time_display_frame,
            textvariable=self.minute_var,
            font=FONTS["display_large"],
            fg=COLORS["primary"],
            bg=COLORS["bg_light"],
            cursor="hand2",
        )
        self.minute_label.pack(side="left")
        self.minute_label.bind("<Button-1>", self._show_minute_picker)

        # AM/PM label (for 12-hour format)
        self.ampm_var = tk.StringVar(value="AM")
        self.ampm_label = tk.Label(
            time_display_frame,
            textvariable=self.ampm_var,
            font=FONTS["subtitle"],
            fg=COLORS["text_sub"],
            bg=COLORS["bg_light"],
            cursor="hand2",
        )
        self.ampm_label.bind("<Button-1>", self._toggle_ampm)

        # Subtitle under time
        time_subtitle = tk.Label(
            inner_frame,
            text="設定執行時間",
            font=FONTS["tiny"],
            fg=COLORS["text_sub"],
            bg=COLORS["bg_light"],
        )
        time_subtitle.pack(pady=(8, 0))

    def _create_weekday_section(self):
        """Create weekday selector with circular buttons"""
        section_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        section_frame.pack(fill="x", pady=(0, 16))

        # Header row
        header_row = tk.Frame(section_frame, bg=COLORS["surface_light"])
        header_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            header_row,
            text="重複週期",
            font=("Microsoft JhengHei UI", 11, "bold"),
            fg=COLORS["text_main"],
            bg=COLORS["surface_light"],
        ).pack(side="left")

        select_all_label = tk.Label(
            header_row,
            text="全選",
            font=FONTS["small"],
            fg=COLORS["primary"],
            bg=COLORS["surface_light"],
            cursor="hand2",
        )
        select_all_label.pack(side="right")
        select_all_label.bind("<Button-1>", self._select_all_days)

        # Day buttons row - evenly distributed
        days_frame = tk.Frame(section_frame, bg=COLORS["surface_light"])
        days_frame.pack(fill="x")

        # Use grid for even distribution
        for i in range(7):
            days_frame.grid_columnconfigure(i, weight=1)

        # Default selected days from config
        for i, name in enumerate(WEEKDAY_NAMES):
            var = tk.BooleanVar(value=(i in DEFAULT_SELECTED_DAYS))
            self.weekday_vars.append(var)

            btn = CircularDayButton(days_frame, text=name, variable=var, size=44)
            btn.grid(row=0, column=i, padx=2, pady=2)

    def _create_repeat_section(self):
        """Create repeat toggle section with rounded corners"""
        # Outer container
        outer_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        outer_frame.pack(fill="x", pady=(0, 16))

        # Create rounded container using canvas
        repeat_canvas = tk.Canvas(
            outer_frame,
            bg=COLORS["surface_light"],
            highlightthickness=0,
            height=REPEAT_CANVAS_HEIGHT,
        )
        repeat_canvas.pack(fill="x")

        # Draw rounded rectangle background
        def draw_rounded_bg(event=None):
            repeat_canvas.delete("bg")
            w = repeat_canvas.winfo_width()
            h = 72
            r = 16
            repeat_canvas.create_arc(
                0,
                0,
                2 * r,
                2 * r,
                start=90,
                extent=90,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            repeat_canvas.create_arc(
                w - 2 * r,
                0,
                w,
                2 * r,
                start=0,
                extent=90,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            repeat_canvas.create_arc(
                0,
                h - 2 * r,
                2 * r,
                h,
                start=180,
                extent=90,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            repeat_canvas.create_arc(
                w - 2 * r,
                h - 2 * r,
                w,
                h,
                start=270,
                extent=90,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            repeat_canvas.create_rectangle(
                r,
                0,
                w - r,
                h,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            repeat_canvas.create_rectangle(
                0,
                r,
                w,
                h - r,
                fill=COLORS["bg_light"],
                outline=COLORS["bg_light"],
                tags="bg",
            )
            repeat_canvas.tag_lower("bg")

        repeat_canvas.bind("<Configure>", draw_rounded_bg)

        inner_frame = tk.Frame(repeat_canvas, bg=COLORS["bg_light"])
        inner_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)

        # Left side - icon and text
        left_frame = tk.Frame(inner_frame, bg=COLORS["bg_light"])
        left_frame.pack(side="left")

        # Icon circle
        icon_canvas = tk.Canvas(
            left_frame, width=40, height=40, bg=COLORS["bg_light"], highlightthickness=0
        )
        icon_canvas.pack(side="left", padx=(0, 12))
        icon_canvas.create_oval(
            2, 2, 38, 38, fill=COLORS["surface_light"], outline=COLORS["surface_light"]
        )
        icon_canvas.create_text(
            20,
            20,
            text="\u21bb",
            font=("Microsoft JhengHei UI", 16),
            fill=COLORS["primary"],
        )

        # Text
        text_frame = tk.Frame(left_frame, bg=COLORS["bg_light"])
        text_frame.pack(side="left")

        tk.Label(
            text_frame,
            text="重複執行",
            font=("Microsoft JhengHei UI", 11, "bold"),
            fg=COLORS["text_main"],
            bg=COLORS["bg_light"],
        ).pack(anchor="w")

        tk.Label(
            text_frame,
            text="每週固定時間執行關機",
            font=FONTS["small"],
            fg=COLORS["text_sub"],
            bg=COLORS["bg_light"],
        ).pack(anchor="w")

        # Right side - toggle
        self.repeat_toggle = ModernToggle(
            inner_frame, variable=self.repeat_var, width=48, height=24
        )
        self.repeat_toggle.pack(side="right")

    def _create_help_section(self):
        """Create collapsible help section with rounded border"""
        # Outer container
        outer_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        outer_frame.pack(fill="x", pady=(0, 16))

        # Create rounded container with border using canvas
        help_canvas = tk.Canvas(
            outer_frame,
            bg=COLORS["surface_light"],
            highlightthickness=0,
            height=HELP_CANVAS_COLLAPSED,
        )
        help_canvas.pack(fill="x")
        self.help_canvas = help_canvas  # Store reference for height updates

        # Draw rounded rectangle with border
        def draw_rounded_border(event=None):
            help_canvas.delete("bg")
            w = help_canvas.winfo_width()
            h = help_canvas.winfo_height()
            r = 16
            # Border
            help_canvas.create_arc(
                0,
                0,
                2 * r,
                2 * r,
                start=90,
                extent=90,
                outline=COLORS["border"],
                style="arc",
                width=1,
                tags="bg",
            )
            help_canvas.create_arc(
                w - 2 * r,
                0,
                w,
                2 * r,
                start=0,
                extent=90,
                outline=COLORS["border"],
                style="arc",
                width=1,
                tags="bg",
            )
            help_canvas.create_arc(
                0,
                h - 2 * r,
                2 * r,
                h,
                start=180,
                extent=90,
                outline=COLORS["border"],
                style="arc",
                width=1,
                tags="bg",
            )
            help_canvas.create_arc(
                w - 2 * r,
                h - 2 * r,
                w,
                h,
                start=270,
                extent=90,
                outline=COLORS["border"],
                style="arc",
                width=1,
                tags="bg",
            )
            help_canvas.create_line(r, 0, w - r, 0, fill=COLORS["border"], tags="bg")
            help_canvas.create_line(r, h, w - r, h, fill=COLORS["border"], tags="bg")
            help_canvas.create_line(0, r, 0, h - r, fill=COLORS["border"], tags="bg")
            help_canvas.create_line(w, r, w, h - r, fill=COLORS["border"], tags="bg")
            # Fill inside
            help_canvas.create_rectangle(
                r,
                1,
                w - r,
                h - 1,
                fill=COLORS["surface_light"],
                outline=COLORS["surface_light"],
                tags="bg",
            )
            help_canvas.create_rectangle(
                1,
                r,
                w - 1,
                h - r,
                fill=COLORS["surface_light"],
                outline=COLORS["surface_light"],
                tags="bg",
            )
            help_canvas.tag_lower("bg")

        help_canvas.bind("<Configure>", draw_rounded_border)

        self.help_section = CollapsibleSection(help_canvas, title="使用說明與提示")
        self.help_section.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)

        # Store original toggle function and override
        original_toggle = self.help_section._toggle

        def new_toggle(event=None):
            original_toggle(event)
            # Update canvas height and window size
            if self.help_section.is_expanded:
                self.help_canvas.config(height=HELP_CANVAS_EXPANDED)
                # Expand window to fit content
                extra_height = HELP_CANVAS_EXPANDED - HELP_CANVAS_COLLAPSED
                self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT + extra_height}")
            else:
                self.help_canvas.config(height=HELP_CANVAS_COLLAPSED)
                # Restore original window size
                self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.help_section._toggle = new_toggle
        self.help_section.header.bind("<Button-1>", new_toggle)
        self.help_section.title_label.bind("<Button-1>", new_toggle)
        self.help_section.arrow_label.bind("<Button-1>", new_toggle)
        self.help_section.icon_label.bind("<Button-1>", new_toggle)

        # Add help content
        for tip in HELP_TIPS:
            tip_label = tk.Label(
                self.help_section.content,
                text=tip,
                font=FONTS["small"],
                fg=COLORS["text_sub"],
                bg=COLORS["bg_light"],
                anchor="w",
                justify="left",
            )
            tip_label.pack(fill="x", padx=8, pady=2)

    def _create_status_section(self):
        """Create status indicator"""
        status_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        status_frame.pack(fill="x", pady=(0, 16))

        self.status_indicator = StatusIndicator(
            status_frame, bg=COLORS["surface_light"]
        )
        self.status_indicator.pack()

    def _create_action_buttons(self):
        """Create action buttons"""
        buttons_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        buttons_frame.pack(fill="x", pady=(8, 0))

        # Primary button - Set shutdown
        self.set_button = ModernButton(
            buttons_frame,
            text="\u23fb  設定關機",
            command=self._schedule_shutdown,
            primary=True,
            width=WINDOW_WIDTH - 40,  # Account for padding
            height=BUTTON_HEIGHT_LARGE,
        )
        self.set_button.pack(pady=(0, PADDING_WIDGET))

        # Secondary buttons row
        secondary_frame = tk.Frame(buttons_frame, bg=COLORS["surface_light"])
        secondary_frame.pack(fill="x")

        self.cancel_button = ModernButton(
            secondary_frame,
            text="\u2715  取消關機",
            command=self._cancel_shutdown,
            primary=False,
            width=182,
            height=BUTTON_HEIGHT_MEDIUM,
        )
        self.cancel_button.pack(side="left")

        self.check_button = ModernButton(
            secondary_frame,
            text="\u2713  檢查排程",
            command=self._check_schedule,
            primary=False,
            width=182,
            height=BUTTON_HEIGHT_MEDIUM,
        )
        self.check_button.pack(side="right")

    def _start_colon_animation(self):
        """Animate the colon blinking"""
        self.colon_visible = not self.colon_visible
        self.colon_label.config(
            fg=COLORS["text_main"] if self.colon_visible else COLORS["bg_light"]
        )
        self.root.after(COLON_BLINK_INTERVAL, self._start_colon_animation)

    def _on_format_change(self):
        """Handle time format change"""
        is_24h = self.time_format_var.get() == "24小時"

        if is_24h:
            self.ampm_label.pack_forget()
            # Convert from 12h to 24h if needed
            hour = int(self.hour_var.get())
            ampm = self.ampm_var.get()

            if ampm == "PM" and hour != 12:
                hour += 12
            elif ampm == "AM" and hour == 12:
                hour = 0

            self.hour_var.set(f"{hour:02d}")
        else:
            self.ampm_label.pack(side="left", padx=(8, 0))
            # Convert from 24h to 12h
            hour = int(self.hour_var.get())
            if hour >= 12:
                self.ampm_var.set("PM")
                if hour > 12:
                    hour -= 12
            else:
                self.ampm_var.set("AM")
                if hour == 0:
                    hour = 12
            self.hour_var.set(f"{hour:02d}")

    def _show_hour_picker(self, event=None):
        """Show hour picker popup"""
        self._show_number_picker(
            self.hour_var, 24 if self.time_format_var.get() == "24小時" else 12, "hour"
        )

    def _show_minute_picker(self, event=None):
        """Show minute picker popup"""
        self._show_number_picker(self.minute_var, 60, "minute")

    def _show_number_picker(self, var, max_val, picker_type):
        """Show a popup number picker"""
        popup = self._create_picker_popup()
        canvas, scrollbar, inner_frame = self._create_scrollable_container(popup)

        start_val, end_val = self._get_picker_range(picker_type, max_val)
        self._create_picker_buttons(inner_frame, var, start_val, end_val, popup)

        self._setup_picker_scrolling(
            canvas, scrollbar, inner_frame, var, start_val, end_val
        )
        self._setup_picker_events(popup)

    def _create_picker_popup(self):
        """Create the popup window for number picker"""
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.configure(bg=COLORS["surface_light"])

        # Position popup near the main window center
        x = self.root.winfo_x() + self.root.winfo_width() // 2 - 50
        y = self.root.winfo_y() + 180
        popup.geometry(f"100x220+{x}+{y}")

        # Add border effect
        border_frame = tk.Frame(popup, bg=COLORS["border"])
        border_frame.pack(fill="both", expand=True, padx=1, pady=1)

        return popup

    def _create_scrollable_container(self, popup):
        """Create scrollable container for picker buttons"""
        inner_container = tk.Frame(popup, bg=COLORS["surface_light"])
        inner_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            inner_container,
            width=80,
            height=200,
            bg=COLORS["surface_light"],
            highlightthickness=0,
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            inner_container, orient="vertical", command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = tk.Frame(canvas, bg=COLORS["surface_light"])
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        return canvas, scrollbar, inner_frame

    def _get_picker_range(self, picker_type, max_val):
        """Get the start and end values for picker based on type"""
        if picker_type == "hour":
            if self.time_format_var.get() == "24小時":
                return 0, max_val
            else:
                return 1, 13
        else:  # minute
            return 0, max_val

    def _create_picker_buttons(self, inner_frame, var, start_val, end_val, popup):
        """Create number selection buttons"""
        current_val = var.get()
        for i in range(start_val, end_val):
            val = f"{i:02d}"
            is_current = val == current_val
            btn = tk.Label(
                inner_frame,
                text=val,
                font=(
                    FONTS["body"] if not is_current else (FONTS["body"][0], 10, "bold")
                ),
                fg=COLORS["primary"] if is_current else COLORS["text_main"],
                bg=COLORS["surface_light"],
                cursor="hand2",
                width=6,
                pady=6,
            )
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, v=val: self._select_number(var, v, popup))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["bg_light"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS["surface_light"]))

    def _setup_picker_scrolling(
        self, canvas, scrollbar, inner_frame, var, start_val, end_val
    ):
        """Setup scrolling and position to current value"""
        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Scroll to current value
        try:
            current_val = var.get()
            current_idx = int(current_val) - start_val
            if current_idx > 0:
                canvas.yview_moveto(
                    max(0, (current_idx - 3) / max(1, end_val - start_val))
                )
        except (ValueError, ZeroDivisionError):
            pass

    def _setup_picker_events(self, popup):
        """Setup popup close events"""

        def close_popup(event=None):
            try:
                popup.destroy()
            except tk.TclError:
                pass

        popup.bind("<Escape>", close_popup)
        popup.bind("<FocusOut>", close_popup)

        # Also close when clicking anywhere on the root window
        def on_root_click(event):
            close_popup()
            self.root.unbind("<Button-1>")

        self.root.bind("<Button-1>", on_root_click)
        popup.focus_set()

    def _select_number(self, var, value, popup):
        """Select a number from picker"""
        var.set(value)
        popup.destroy()

    def _toggle_ampm(self, event=None):
        """Toggle AM/PM"""
        current = self.ampm_var.get()
        self.ampm_var.set("PM" if current == "AM" else "AM")

    def _select_all_days(self, event=None):
        """Select or deselect all days"""
        all_selected = all(var.get() for var in self.weekday_vars)
        for var in self.weekday_vars:
            var.set(not all_selected)

    def _get_time_24h(self):
        """Get time in 24-hour format"""
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())

        if self.time_format_var.get() == "12小時":
            if self.ampm_var.get() == "PM" and hour != 12:
                hour += 12
            elif self.ampm_var.get() == "AM" and hour == 12:
                hour = 0

        return f"{hour:02d}:{minute:02d}"

    def _schedule_shutdown(self):
        """Schedule system shutdown"""
        try:
            time_str = self._get_time_24h()
            selected_days = self._get_selected_days()

            if not selected_days:
                self._show_validation_error(MESSAGES["validation_error"])
                return

            is_repeat = self.repeat_var.get()
            self.scheduler.create_schedule(selected_days, time_str, is_repeat)

            self._update_status("active", MESSAGES["active_status"])
            # Ensure UI updates are processed before showing messagebox
            self.root.update_idletasks()
            self._show_success_message(MESSAGES["success_scheduled"])

        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            self._show_validation_error(str(e))
        except PermissionError as e:
            logger.error(f"Permission denied: {str(e)}")
            self._show_permission_error()
        except Exception as e:
            logger.error(f"Failed to schedule shutdown: {str(e)}")
            self._show_general_error("設定排程失敗", str(e))

    def _get_selected_days(self):
        """Get list of selected weekdays"""
        return [i + 1 for i, var in enumerate(self.weekday_vars) if var.get()]

    def _show_validation_error(self, message):
        """Show validation error message"""
        messagebox.showerror(MESSAGES["input_error"], message)

    def _show_permission_error(self):
        """Show permission error message with help"""
        messagebox.showerror(MESSAGES["error_title"], MESSAGES["permission_error"])

    def _show_general_error(self, title, message):
        """Show general error message"""
        messagebox.showerror(title, message)

    def _show_success_message(self, message):
        """Show success message"""
        messagebox.showinfo(MESSAGES["success_title"], message)

    def _cancel_shutdown(self):
        """Cancel scheduled shutdown"""
        try:
            self.scheduler.remove_schedule()
            self._update_status("inactive", MESSAGES["inactive_status"])
            messagebox.showinfo(MESSAGES["success_title"], MESSAGES["success_canceled"])
        except Exception as e:
            logger.error(f"Failed to cancel shutdown: {str(e)}")
            messagebox.showerror(MESSAGES["error_title"], str(e))

    def _check_schedule(self):
        """Check current schedule status"""
        try:
            task_info = self.scheduler.get_schedule_info()
            if task_info and "找不到" not in task_info:
                self._update_status("active", MESSAGES["active_status"])
            else:
                self._update_status("inactive", MESSAGES["inactive_status"])
            messagebox.showinfo(MESSAGES["schedule_status"], task_info)
        except Exception as e:
            logger.error(f"Failed to check schedule: {str(e)}")
            messagebox.showerror(MESSAGES["error_title"], str(e))

    def _update_status(self, status, text):
        """Update status indicator"""
        self.status_indicator.set_status(status, text)

    def _parse_schedule_time_from_info(self, task_info):
        """Parse time and weekdays from task scheduler info string"""
        import re
        result = {"time": None, "weekdays": None}
        
        if not task_info or "找不到" in task_info:
            return result
            
        try:
            # Parse next run time - formats like "2026/1/14 23:30:00" or "2026-01-14 23:30:00"
            next_run_patterns = [
                r"下次執行時間[：:]\s*([\d/\-]+)\s+(\d{1,2}[：:]\d{2})",
                r"Next Run Time[：:]\s*([\d/\-]+)\s+(\d{1,2}[：:]\d{2})",
            ]
            
            for pattern in next_run_patterns:
                match = re.search(pattern, task_info)
                if match:
                    time_str = match.group(2).replace("：", ":")
                    parts = time_str.split(":")
                    if len(parts) >= 2:
                        result["time"] = f"{int(parts[0]):02d}:{int(parts[1]):02d}"
                        break
            
            logger.info(f"Parsed schedule info: {result}")
        except Exception as e:
            logger.warning(f"Failed to parse schedule info: {e}")
            
        return result

    def _load_saved_config(self):
        """Load saved configuration"""
        # 檢查是否有執行中的排程
        has_active = self.scheduler.has_active_schedule()
        config = self.scheduler.load_config()

        # 如果有執行中的排程，無論是否有設定檔，都顯示為已啟用
        if has_active:
            self._update_status("active", "已設定排程")

        # 嘗試載入設定
        config_loaded = False
        if config:
            try:
                # Set weekday checkboxes
                saved_weekdays = config.get("weekdays", [])
                if saved_weekdays:
                    if all(isinstance(x, bool) for x in saved_weekdays):
                        for var, enabled in zip(self.weekday_vars, saved_weekdays):
                            var.set(enabled)
                    else:
                        try:
                            days = [int(x) for x in saved_weekdays]
                            for i, var in enumerate(self.weekday_vars):
                                var.set((i + 1) in days)
                        except Exception:
                            logger.debug(
                                "Unexpected format for saved weekdays, ignoring"
                            )

                # Set time
                time_str = config.get("time")
                if time_str:
                    hour, minute = map(int, time_str.split(":"))
                    self.hour_var.set(f"{hour:02d}")
                    self.minute_var.set(f"{minute:02d}")

                # Set execution mode
                self.repeat_var.set(config.get("is_repeat", True))
                
                config_loaded = True

            except Exception:
                logger.exception("Failed to load configuration")

        # 如果沒有載入設定但有活躍排程，嘗試從 Windows 任務排程器解析時間
        if not config_loaded and has_active:
            try:
                task_info = self.scheduler.get_schedule_info()
                parsed = self._parse_schedule_time_from_info(task_info)
                
                if parsed["time"]:
                    hour, minute = map(int, parsed["time"].split(":"))
                    self.hour_var.set(f"{hour:02d}")
                    self.minute_var.set(f"{minute:02d}")
                    config_loaded = True
                    logger.info(f"Loaded time from scheduler: {parsed['time']}")
            except Exception as e:
                logger.warning(f"Failed to parse schedule from task info: {e}")

        # 如果仍然沒有載入設定（首次執行），使用預設值
        if not config_loaded:
            now = datetime.now()

            # 設定當前時間
            self.hour_var.set(f"{now.hour:02d}")
            self.minute_var.set(f"{now.minute:02d}")

            # 設定當天星期（weekday() 返回 0-6，0是星期一）
            today_weekday = now.weekday()
            for i, var in enumerate(self.weekday_vars):
                var.set(i == today_weekday)

            logger.info(
                f"Auto-selected today ({WEEKDAY_NAMES[today_weekday]}) and current time {now.hour:02d}:{now.minute:02d}"
            )

    def run(self):
        """Start the application"""
        self.root.mainloop()
