"""Modern custom widgets for the auto shutdown application"""
import tkinter as tk
from .modern_theme import COLORS, FONTS


class RoundedFrame(tk.Canvas):
    """具有圓角的框架"""

    def __init__(self, parent, bg_color=None, corner_radius=16, **kwargs):
        self.bg_color = bg_color or COLORS["surface_light"]
        self.corner_radius = corner_radius

        super().__init__(
            parent,
            bg=parent.cget("bg") if hasattr(parent, "cget") else COLORS["surface_light"],
            highlightthickness=0,
            **kwargs
        )

        self.bind("<Configure>", self._draw_rounded_rect)

    def _draw_rounded_rect(self, event=None):
        self.delete("rounded_bg")
        w, h = self.winfo_width(), self.winfo_height()
        r = self.corner_radius

        # 繪製圓角矩形
        self.create_polygon(
            r, 0, w - r, 0,
            w, 0, w, r,
            w, h - r, w, h,
            w - r, h, r, h,
            0, h, 0, h - r,
            0, r, 0, 0,
            smooth=True,
            fill=self.bg_color,
            tags="rounded_bg"
        )

        # 使用弧線繪製角落
        self.create_arc(0, 0, 2 * r, 2 * r, start=90, extent=90, fill=self.bg_color, outline=self.bg_color, tags="rounded_bg")
        self.create_arc(w - 2 * r, 0, w, 2 * r, start=0, extent=90, fill=self.bg_color, outline=self.bg_color, tags="rounded_bg")
        self.create_arc(0, h - 2 * r, 2 * r, h, start=180, extent=90, fill=self.bg_color, outline=self.bg_color, tags="rounded_bg")
        self.create_arc(w - 2 * r, h - 2 * r, w, h, start=270, extent=90, fill=self.bg_color, outline=self.bg_color, tags="rounded_bg")

        # 填充中心區域
        self.create_rectangle(r, 0, w - r, h, fill=self.bg_color, outline=self.bg_color, tags="rounded_bg")
        self.create_rectangle(0, r, w, h - r, fill=self.bg_color, outline=self.bg_color, tags="rounded_bg")

        self.tag_lower("rounded_bg")


class ModernToggle(tk.Canvas):
    """現代化切換開關元件"""

    def __init__(self, parent, variable=None, command=None, **kwargs):
        self.width = kwargs.pop("width", 48)
        self.height = kwargs.pop("height", 24)

        super().__init__(
            parent,
            width=self.width,
            height=self.height,
            bg=parent.cget("bg") if hasattr(parent, "cget") else COLORS["surface_light"],
            highlightthickness=0,
            **kwargs
        )

        self.variable = variable or tk.BooleanVar(value=False)
        self.command = command
        self.knob_padding = 2
        self.knob_size = self.height - (self.knob_padding * 2)

        self._draw()
        self.bind("<Button-1>", self._toggle)
        self.variable.trace_add("write", lambda *args: self._draw())

    def _draw(self):
        self.delete("all")
        is_on = self.variable.get()

        # 軌道顏色
        track_color = COLORS["primary"] if is_on else COLORS["inactive"]

        # 繪製軌道（圓角矩形）
        r = self.height // 2
        self.create_arc(0, 0, self.height, self.height, start=90, extent=180, fill=track_color, outline=track_color)
        self.create_arc(self.width - self.height, 0, self.width, self.height, start=270, extent=180, fill=track_color, outline=track_color)
        self.create_rectangle(r, 0, self.width - r, self.height, fill=track_color, outline=track_color)

        # 繪製圓鈕
        knob_x = self.width - self.height + self.knob_padding if is_on else self.knob_padding
        self.create_oval(
            knob_x, self.knob_padding,
            knob_x + self.knob_size, self.knob_padding + self.knob_size,
            fill=COLORS["text_white"],
            outline=COLORS["text_white"]
        )

    def _toggle(self, event=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()


class PillToggle(tk.Canvas):
    """膠囊樣式切換器，用於24小時/12小時等選項"""

    def __init__(self, parent, options, variable=None, command=None, **kwargs):
        self.options = options
        self.button_width = kwargs.pop("button_width", 60)
        self.button_height = kwargs.pop("button_height", 28)
        self.padding = 3

        total_width = len(options) * self.button_width + self.padding * 2
        total_height = self.button_height + self.padding * 2

        super().__init__(
            parent,
            width=total_width,
            height=total_height,
            bg=parent.cget("bg") if hasattr(parent, "cget") else COLORS["bg_light"],
            highlightthickness=0,
            **kwargs
        )

        self.variable = variable or tk.StringVar(value=options[0])
        self.command = command

        self._draw()
        self.bind("<Button-1>", self._on_click)
        self.variable.trace_add("write", lambda *args: self._draw())

    def _draw(self):
        self.delete("all")

        # 繪製背景膠囊
        r = (self.button_height + self.padding * 2) // 2
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()

        # 背景
        self.create_arc(0, 0, h, h, start=90, extent=180, fill=COLORS["surface_light"], outline=COLORS["surface_light"])
        self.create_arc(w - h, 0, w, h, start=270, extent=180, fill=COLORS["surface_light"], outline=COLORS["surface_light"])
        self.create_rectangle(r, 0, w - r, h, fill=COLORS["surface_light"], outline=COLORS["surface_light"])

        selected = self.variable.get()

        for i, opt in enumerate(self.options):
            x = self.padding + i * self.button_width
            is_selected = opt == selected

            if is_selected:
                # 繪製選中的膠囊
                br = self.button_height // 2
                self.create_arc(x, self.padding, x + self.button_height, self.padding + self.button_height,
                                start=90, extent=180, fill=COLORS["primary"], outline=COLORS["primary"])
                self.create_arc(x + self.button_width - self.button_height, self.padding,
                                x + self.button_width, self.padding + self.button_height,
                                start=270, extent=180, fill=COLORS["primary"], outline=COLORS["primary"])
                self.create_rectangle(x + br, self.padding, x + self.button_width - br,
                                       self.padding + self.button_height, fill=COLORS["primary"], outline=COLORS["primary"])

            # 繪製文字
            text_color = COLORS["text_white"] if is_selected else COLORS["text_sub"]
            self.create_text(
                x + self.button_width // 2,
                self.padding + self.button_height // 2,
                text=opt,
                fill=text_color,
                font=FONTS["small"]
            )

    def _on_click(self, event):
        # 判斷點擊了哪個選項
        for i, opt in enumerate(self.options):
            x_start = self.padding + i * self.button_width
            x_end = x_start + self.button_width
            if x_start <= event.x <= x_end:
                self.variable.set(opt)
                if self.command:
                    self.command()
                break


class CircularDayButton(tk.Canvas):
    """圓形按鈕，用於日期選擇"""

    def __init__(self, parent, text, variable=None, command=None, **kwargs):
        self.size = kwargs.pop("size", 40)
        self.text = text

        super().__init__(
            parent,
            width=self.size,
            height=self.size,
            bg=parent.cget("bg") if hasattr(parent, "cget") else COLORS["bg_light"],
            highlightthickness=0,
            **kwargs
        )

        self.variable = variable or tk.BooleanVar(value=False)
        self.command = command

        self._draw()
        self.bind("<Button-1>", self._toggle)
        self.variable.trace_add("write", lambda *args: self._draw())

    def _draw(self):
        self.delete("all")
        is_selected = self.variable.get()

        # 圓形
        fill_color = COLORS["primary"] if is_selected else COLORS["surface_light"]
        outline_color = COLORS["primary"] if is_selected else COLORS["border"]

        self.create_oval(
            1, 1, self.size - 1, self.size - 1,
            fill=fill_color,
            outline=outline_color,
            width=1
        )

        # 文字
        text_color = COLORS["text_white"] if is_selected else COLORS["text_sub"]
        self.create_text(
            self.size // 2,
            self.size // 2,
            text=self.text,
            fill=text_color,
            font=FONTS["body"]
        )

    def _toggle(self, event=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()


class ModernButton(tk.Canvas):
    """現代化圓角按鈕，支援可選圖標和陰影效果"""

    def __init__(self, parent, text, command=None, primary=True, icon=None, **kwargs):
        self.text = text
        self.command = command
        self.primary = primary
        self.icon = icon
        self.width = kwargs.pop("width", 200)
        self.height = kwargs.pop("height", 44)

        # 如果是主要按鈕，為陰影增加額外高度
        canvas_height = self.height + (4 if primary else 0)

        super().__init__(
            parent,
            width=self.width,
            height=canvas_height,
            bg=parent.cget("bg") if hasattr(parent, "cget") else COLORS["surface_light"],
            highlightthickness=0,
            **kwargs
        )

        self.is_hovered = False
        self.is_pressed = False
        self._draw()

        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self):
        self.delete("all")

        if self.primary:
            fill_color = COLORS["primary_dark"] if self.is_hovered else COLORS["primary"]
            shadow_color = "#4338ca"  # 陰影用深紫色
        else:
            fill_color = COLORS["border"] if self.is_hovered else COLORS["bg_light"]
            shadow_color = None

        text_color = COLORS["text_white"] if self.primary else COLORS["text_main"]

        r = 12
        w, h = self.width, self.height
        y_offset = 2 if self.is_pressed and self.primary else 0

        # 為主要按鈕繪製陰影
        if self.primary and not self.is_pressed:
            shadow_y = 4
            self._draw_rounded_rect(0, shadow_y, w, h + shadow_y, r, shadow_color)

        # 繪製主按鈕
        self._draw_rounded_rect(0, y_offset, w, h + y_offset, r, fill_color)

        # 繪製文字
        display_text = self.text

        self.create_text(
            w // 2,
            (h // 2) + y_offset,
            text=display_text,
            fill=text_color,
            font=FONTS["button"]
        )

    def _draw_rounded_rect(self, x, y, w, h, r, fill_color):
        """繪製圓角矩形的輔助函數"""
        self.create_arc(x, y, x + 2 * r, y + 2 * r, start=90, extent=90, fill=fill_color, outline=fill_color)
        self.create_arc(w - 2 * r, y, w, y + 2 * r, start=0, extent=90, fill=fill_color, outline=fill_color)
        self.create_arc(x, h - 2 * r, x + 2 * r, h, start=180, extent=90, fill=fill_color, outline=fill_color)
        self.create_arc(w - 2 * r, h - 2 * r, w, h, start=270, extent=90, fill=fill_color, outline=fill_color)
        self.create_rectangle(x + r, y, w - r, h, fill=fill_color, outline=fill_color)
        self.create_rectangle(x, y + r, w, h - r, fill=fill_color, outline=fill_color)

    def _on_click(self, event):
        self.is_pressed = True
        self._draw()

    def _on_release(self, event):
        self.is_pressed = False
        self._draw()
        if self.command:
            # 檢查釋放是否在按鈕範圍內
            if 0 <= event.x <= self.width and 0 <= event.y <= self.height:
                self.command()

    def _on_enter(self, event):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw()


class CollapsibleSection(tk.Frame):
    """可折疊的區段，帶有標頭"""

    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, bg=COLORS["surface_light"], **kwargs)

        self.is_expanded = False

        # 標頭框架
        self.header = tk.Frame(self, bg=COLORS["surface_light"], cursor="hand2")
        self.header.pack(fill="x", padx=0, pady=0)

        # 圖標
        self.icon_label = tk.Label(
            self.header,
            text="\u24d8",  # Info circle
            font=FONTS["body"],
            fg=COLORS["text_sub"],
            bg=COLORS["surface_light"]
        )
        self.icon_label.pack(side="left", padx=(0, 8))

        # 標題
        self.title_label = tk.Label(
            self.header,
            text=title,
            font=FONTS["body"],
            fg=COLORS["text_main"],
            bg=COLORS["surface_light"]
        )
        self.title_label.pack(side="left")

        # 箭頭
        self.arrow_label = tk.Label(
            self.header,
            text="\u25bc",
            font=FONTS["small"],
            fg=COLORS["text_sub"],
            bg=COLORS["surface_light"]
        )
        self.arrow_label.pack(side="right")

        # 內容框架
        self.content = tk.Frame(self, bg=COLORS["bg_light"])

        # 綁定事件
        self.header.bind("<Button-1>", self._toggle)
        self.title_label.bind("<Button-1>", self._toggle)
        self.arrow_label.bind("<Button-1>", self._toggle)
        self.icon_label.bind("<Button-1>", self._toggle)

    def _toggle(self, event=None):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.content.pack(fill="x", pady=(8, 0))
            self.arrow_label.config(text="\u25b2")
        else:
            self.content.forget()
            self.arrow_label.config(text="\u25bc")

    def add_content(self, widget):
        """將元件加入內容區域"""
        widget.pack(in_=self.content, fill="x", padx=16, pady=4)


class StatusIndicator(tk.Frame):
    """帶有彩色圓點的狀態指示器"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=kwargs.pop("bg", COLORS["surface_light"]), **kwargs)

        self.dot = tk.Canvas(
            self,
            width=10,
            height=10,
            bg=self.cget("bg"),
            highlightthickness=0
        )
        self.dot.pack(side="left", padx=(0, 6))

        self.label = tk.Label(
            self,
            text="",
            font=FONTS["small"],
            fg=COLORS["text_sub"],
            bg=self.cget("bg")
        )
        self.label.pack(side="left")

        self.set_status("inactive", "未設定排程")

    def set_status(self, status, text):
        """設定狀態：'active'、'inactive'、'warning'、'error'"""
        colors = {
            "active": COLORS["success"],
            "inactive": COLORS["error"],
            "warning": COLORS["warning"],
            "error": COLORS["error"]
        }

        self.dot.delete("all")
        color = colors.get(status, COLORS["inactive"])
        self.dot.create_oval(1, 1, 9, 9, fill=color, outline=color)
        self.label.config(text=f"目前狀態：{text}")
