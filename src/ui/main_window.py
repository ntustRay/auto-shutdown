"""Modern main window for the auto shutdown application"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from ..scheduler import ShutdownScheduler
from .modern_theme import COLORS, FONTS, configure_styles
from .modern_widgets import (
    PillToggle, CircularDayButton, ModernToggle,
    ModernButton, CollapsibleSection, StatusIndicator
)
import logging

logger = logging.getLogger(__name__)


class AutoShutdownWindow:
    """Modern application window for auto shutdown scheduling"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("自動關機系統")
        self.root.geometry("420x750")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg_light"])

        # Configure styles
        configure_styles()

        self.scheduler = ShutdownScheduler()
        self.weekday_vars = []
        self.weekday_names = ["一", "二", "三", "四", "五", "六", "日"]
        self.weekday_full_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

        # Time variables (default to 23:28 matching spec)
        self.hour_var = tk.StringVar(value="23")
        self.minute_var = tk.StringVar(value="28")
        self.time_format_var = tk.StringVar(value="24小時")
        self.repeat_var = tk.BooleanVar(value=True)

        # Animation state
        self.colon_visible = True

        self._create_ui()
        self._load_saved_config()
        self._start_colon_animation()

    def _create_ui(self):
        """Create the modern user interface"""
        # Main container
        self.main_container = tk.Frame(self.root, bg=COLORS["surface_light"])
        self.main_container.pack(fill="both", expand=True, padx=16, pady=16)

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
        header_frame.pack(fill="x", pady=(8, 20))

        title = tk.Label(
            header_frame,
            text="自動關機系統",
            font=FONTS["title"],
            fg=COLORS["text_main"],
            bg=COLORS["surface_light"]
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header_frame,
            text="智慧排程管理您的設備",
            font=FONTS["subtitle"],
            fg=COLORS["text_sub"],
            bg=COLORS["surface_light"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _create_time_section(self):
        """Create the time display and format toggle"""
        # Outer container for rounded effect
        outer_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        outer_frame.pack(fill="x", pady=(0, 20))

        # Create rounded container using canvas
        time_canvas = tk.Canvas(
            outer_frame,
            bg=COLORS["surface_light"],
            highlightthickness=0,
            height=200
        )
        time_canvas.pack(fill="x")

        # Draw rounded rectangle background
        def draw_rounded_bg(event=None):
            time_canvas.delete("bg")
            w = time_canvas.winfo_width()
            h = 200
            r = 16
            # Draw rounded rectangle
            time_canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            time_canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            time_canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            time_canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            time_canvas.create_rectangle(r, 0, w-r, h, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            time_canvas.create_rectangle(0, r, w, h-r, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            # Top accent line
            time_canvas.create_rectangle(0, 0, w, 3, fill=COLORS["primary"], outline=COLORS["primary"], tags="bg")
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
            button_height=26
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
            cursor="hand2"
        )
        self.hour_label.pack(side="left")
        self.hour_label.bind("<Button-1>", self._show_hour_picker)

        # Colon
        self.colon_label = tk.Label(
            time_display_frame,
            text=":",
            font=FONTS["display_large"],
            fg=COLORS["text_main"],
            bg=COLORS["bg_light"]
        )
        self.colon_label.pack(side="left")

        # Minute
        self.minute_label = tk.Label(
            time_display_frame,
            textvariable=self.minute_var,
            font=FONTS["display_large"],
            fg=COLORS["primary"],
            bg=COLORS["bg_light"],
            cursor="hand2"
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
            cursor="hand2"
        )
        self.ampm_label.bind("<Button-1>", self._toggle_ampm)

        # Subtitle under time
        time_subtitle = tk.Label(
            inner_frame,
            text="設定執行時間",
            font=FONTS["tiny"],
            fg=COLORS["text_sub"],
            bg=COLORS["bg_light"]
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
            bg=COLORS["surface_light"]
        ).pack(side="left")

        select_all_label = tk.Label(
            header_row,
            text="全選",
            font=FONTS["small"],
            fg=COLORS["primary"],
            bg=COLORS["surface_light"],
            cursor="hand2"
        )
        select_all_label.pack(side="right")
        select_all_label.bind("<Button-1>", self._select_all_days)

        # Day buttons row - evenly distributed
        days_frame = tk.Frame(section_frame, bg=COLORS["surface_light"])
        days_frame.pack(fill="x")

        # Use grid for even distribution
        for i in range(7):
            days_frame.grid_columnconfigure(i, weight=1)

        # Default: 一(index 0) and 五(index 4) selected per spec
        default_selected = {0, 4}
        for i, name in enumerate(self.weekday_names):
            var = tk.BooleanVar(value=(i in default_selected))
            self.weekday_vars.append(var)

            btn = CircularDayButton(
                days_frame,
                text=name,
                variable=var,
                size=44
            )
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
            height=72
        )
        repeat_canvas.pack(fill="x")

        # Draw rounded rectangle background
        def draw_rounded_bg(event=None):
            repeat_canvas.delete("bg")
            w = repeat_canvas.winfo_width()
            h = 72
            r = 16
            repeat_canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            repeat_canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            repeat_canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            repeat_canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            repeat_canvas.create_rectangle(r, 0, w-r, h, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            repeat_canvas.create_rectangle(0, r, w, h-r, fill=COLORS["bg_light"], outline=COLORS["bg_light"], tags="bg")
            repeat_canvas.tag_lower("bg")

        repeat_canvas.bind("<Configure>", draw_rounded_bg)

        inner_frame = tk.Frame(repeat_canvas, bg=COLORS["bg_light"])
        inner_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)

        # Left side - icon and text
        left_frame = tk.Frame(inner_frame, bg=COLORS["bg_light"])
        left_frame.pack(side="left")

        # Icon circle
        icon_canvas = tk.Canvas(
            left_frame,
            width=40,
            height=40,
            bg=COLORS["bg_light"],
            highlightthickness=0
        )
        icon_canvas.pack(side="left", padx=(0, 12))
        icon_canvas.create_oval(2, 2, 38, 38, fill=COLORS["surface_light"], outline=COLORS["surface_light"])
        icon_canvas.create_text(20, 20, text="\u21bb", font=("Microsoft JhengHei UI", 16), fill=COLORS["primary"])

        # Text
        text_frame = tk.Frame(left_frame, bg=COLORS["bg_light"])
        text_frame.pack(side="left")

        tk.Label(
            text_frame,
            text="重複執行",
            font=("Microsoft JhengHei UI", 11, "bold"),
            fg=COLORS["text_main"],
            bg=COLORS["bg_light"]
        ).pack(anchor="w")

        tk.Label(
            text_frame,
            text="每週固定時間執行關機",
            font=FONTS["small"],
            fg=COLORS["text_sub"],
            bg=COLORS["bg_light"]
        ).pack(anchor="w")

        # Right side - toggle
        self.repeat_toggle = ModernToggle(
            inner_frame,
            variable=self.repeat_var,
            width=48,
            height=24
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
            height=50
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
            help_canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, outline=COLORS["border"], style="arc", width=1, tags="bg")
            help_canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, outline=COLORS["border"], style="arc", width=1, tags="bg")
            help_canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, outline=COLORS["border"], style="arc", width=1, tags="bg")
            help_canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, outline=COLORS["border"], style="arc", width=1, tags="bg")
            help_canvas.create_line(r, 0, w-r, 0, fill=COLORS["border"], tags="bg")
            help_canvas.create_line(r, h, w-r, h, fill=COLORS["border"], tags="bg")
            help_canvas.create_line(0, r, 0, h-r, fill=COLORS["border"], tags="bg")
            help_canvas.create_line(w, r, w, h-r, fill=COLORS["border"], tags="bg")
            # Fill inside
            help_canvas.create_rectangle(r, 1, w-r, h-1, fill=COLORS["surface_light"], outline=COLORS["surface_light"], tags="bg")
            help_canvas.create_rectangle(1, r, w-1, h-r, fill=COLORS["surface_light"], outline=COLORS["surface_light"], tags="bg")
            help_canvas.tag_lower("bg")

        help_canvas.bind("<Configure>", draw_rounded_border)

        self.help_section = CollapsibleSection(
            help_canvas,
            title="使用說明與提示"
        )
        self.help_section.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)

        # Store original toggle function and override
        original_toggle = self.help_section._toggle
        def new_toggle(event=None):
            original_toggle(event)
            # Update canvas height
            if self.help_section.is_expanded:
                self.help_canvas.config(height=130)
            else:
                self.help_canvas.config(height=50)
        self.help_section._toggle = new_toggle
        self.help_section.header.bind("<Button-1>", new_toggle)
        self.help_section.title_label.bind("<Button-1>", new_toggle)
        self.help_section.arrow_label.bind("<Button-1>", new_toggle)
        self.help_section.icon_label.bind("<Button-1>", new_toggle)

        # Add help content
        tips = [
            "• 選擇要執行的星期 (可複選)",
            "• 系統會在關機前1分鐘顯示提醒",
            "• 設定會自動保存，重開機後依然有效"
        ]

        for tip in tips:
            tip_label = tk.Label(
                self.help_section.content,
                text=tip,
                font=FONTS["small"],
                fg=COLORS["text_sub"],
                bg=COLORS["bg_light"],
                anchor="w",
                justify="left"
            )
            tip_label.pack(fill="x", padx=8, pady=2)

    def _create_status_section(self):
        """Create status indicator"""
        status_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        status_frame.pack(fill="x", pady=(0, 16))

        self.status_indicator = StatusIndicator(status_frame, bg=COLORS["surface_light"])
        self.status_indicator.pack()

    def _create_action_buttons(self):
        """Create action buttons"""
        buttons_frame = tk.Frame(self.main_container, bg=COLORS["surface_light"])
        buttons_frame.pack(fill="x", pady=(8, 0))

        # Primary button - Set shutdown
        self.set_button = ModernButton(
            buttons_frame,
            text="\u23FB  設定關機",
            command=self._schedule_shutdown,
            primary=True,
            width=380,
            height=48
        )
        self.set_button.pack(pady=(0, 12))

        # Secondary buttons row
        secondary_frame = tk.Frame(buttons_frame, bg=COLORS["surface_light"])
        secondary_frame.pack(fill="x")

        self.cancel_button = ModernButton(
            secondary_frame,
            text="\u2715  取消關機",
            command=self._cancel_shutdown,
            primary=False,
            width=182,
            height=40
        )
        self.cancel_button.pack(side="left")

        self.check_button = ModernButton(
            secondary_frame,
            text="\u2713  檢查排程",
            command=self._check_schedule,
            primary=False,
            width=182,
            height=40
        )
        self.check_button.pack(side="right")

    def _start_colon_animation(self):
        """Animate the colon blinking"""
        self.colon_visible = not self.colon_visible
        self.colon_label.config(fg=COLORS["text_main"] if self.colon_visible else COLORS["bg_light"])
        self.root.after(500, self._start_colon_animation)

    def _on_format_change(self):
        """Handle time format change"""
        is_24h = self.time_format_var.get() == "24小時"

        if is_24h:
            self.ampm_label.pack_forget()
            # Convert from 12h to 24h if needed
            hour = int(self.hour_var.get())
            if self.ampm_var.get() == "PM" and hour != 12:
                hour += 12
            elif self.ampm_var.get() == "AM" and hour == 12:
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
            self.hour_var,
            24 if self.time_format_var.get() == "24小時" else 12,
            "hour"
        )

    def _show_minute_picker(self, event=None):
        """Show minute picker popup"""
        self._show_number_picker(self.minute_var, 60, "minute")

    def _show_number_picker(self, var, max_val, picker_type):
        """Show a popup number picker"""
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

        inner_container = tk.Frame(border_frame, bg=COLORS["surface_light"])
        inner_container.pack(fill="both", expand=True)

        # Create scrollable frame
        canvas = tk.Canvas(inner_container, width=80, height=200, bg=COLORS["surface_light"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(inner_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = tk.Frame(canvas, bg=COLORS["surface_light"])
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        start_val = 0 if picker_type == "hour" and self.time_format_var.get() == "24小時" else (1 if picker_type == "hour" else 0)
        end_val = max_val if picker_type == "minute" else (max_val if self.time_format_var.get() == "24小時" else 13)

        current_val = var.get()
        for i in range(start_val, end_val):
            val = f"{i:02d}"
            is_current = val == current_val
            btn = tk.Label(
                inner_frame,
                text=val,
                font=FONTS["body"] if not is_current else ("Microsoft JhengHei UI", 10, "bold"),
                fg=COLORS["primary"] if is_current else COLORS["text_main"],
                bg=COLORS["surface_light"],
                cursor="hand2",
                width=6,
                pady=6
            )
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, v=val: self._select_number(var, v, popup))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["bg_light"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS["surface_light"]))

        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Scroll to current value
        try:
            current_idx = int(current_val) - start_val
            if current_idx > 0:
                canvas.yview_moveto(max(0, (current_idx - 3) / max(1, end_val - start_val)))
        except (ValueError, ZeroDivisionError):
            pass

        # Close popup when clicking outside or pressing Escape
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

            selected_days = [i + 1 for i, var in enumerate(self.weekday_vars) if var.get()]
            if not selected_days:
                raise ValueError("請至少選擇一個星期")

            is_repeat = self.repeat_var.get()
            self.scheduler.create_schedule(selected_days, time_str, is_repeat)

            self._update_status("active", "已設定排程")
            messagebox.showinfo("成功", "已成功設定關機排程")

        except Exception as e:
            logger.error(f"Failed to schedule shutdown: {str(e)}")
            messagebox.showerror("錯誤", str(e))

    def _cancel_shutdown(self):
        """Cancel scheduled shutdown"""
        try:
            self.scheduler.remove_schedule()
            self._update_status("inactive", "未設定排程")
            messagebox.showinfo("成功", "已取消關機排程")
        except Exception as e:
            logger.error(f"Failed to cancel shutdown: {str(e)}")
            messagebox.showerror("錯誤", str(e))

    def _check_schedule(self):
        """Check current schedule status"""
        try:
            task_info = self.scheduler.get_schedule_info()
            if task_info and "找不到" not in task_info:
                self._update_status("active", "已設定排程")
            else:
                self._update_status("inactive", "未設定排程")
            messagebox.showinfo("排程狀態", task_info)
        except Exception as e:
            logger.error(f"Failed to check schedule: {str(e)}")
            messagebox.showerror("錯誤", str(e))

    def _update_status(self, status, text):
        """Update status indicator"""
        self.status_indicator.set_status(status, text)

    def _load_saved_config(self):
        """Load saved configuration"""
        config = self.scheduler.load_config()
        if not config:
            # No config, keep default status as inactive
            return

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
                        logger.debug("Unexpected format for saved weekdays, ignoring")

            # Set time
            time_str = config.get("time")
            if time_str:
                hour, minute = map(int, time_str.split(":"))
                self.hour_var.set(f"{hour:02d}")
                self.minute_var.set(f"{minute:02d}")

            # Set execution mode
            self.repeat_var.set(config.get("is_repeat", True))

            # Only mark as active if we successfully loaded a valid config
            if saved_weekdays and time_str:
                self._update_status("active", "已設定排程")

        except Exception:
            logger.exception("Failed to load configuration")

    def run(self):
        """Start the application"""
        self.root.mainloop()
