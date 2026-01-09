"""Main window for the auto shutdown application"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from .enhanced_time_frame import EnhancedTimeFrame
from ..scheduler import ShutdownScheduler
import logging

logger = logging.getLogger(__name__)

class AutoShutdownWindow:
    """Main application window for auto shutdown scheduling"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("自動關機系統")
        self.root.geometry("500x600")
        
        self.scheduler = ShutdownScheduler()
        self.weekday_vars = []
        self.weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        
        self._create_ui()
        self._load_saved_config()
    def _create_ui(self):
        """Create user interface"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both", padx=10, pady=5)
        
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="關機設定")
        
        self._create_weekday_selector(main_frame)
        self._create_time_selector(main_frame)
        self._create_mode_selector(main_frame)
        self._create_control_buttons(main_frame)
        self._create_status_display(main_frame)
        self._create_help_section(main_frame)
    
    def _create_weekday_selector(self, parent):
        """Create weekday selection frame"""
        frame = ttk.LabelFrame(parent, text="選擇執行星期", padding="10")
        frame.pack(fill="x", padx=10, pady=5)
        
        for i, name in enumerate(self.weekday_names):
            var = tk.BooleanVar()
            self.weekday_vars.append(var)
            cb = ttk.Checkbutton(frame, text=name, variable=var)
            cb.grid(row=i//4, column=i%4, padx=5, pady=2, sticky="w")
    
    def _create_time_selector(self, parent):
        """Create time selection frame"""
        self.time_frame = EnhancedTimeFrame(parent, text="設定時間", padding="10")
        self.time_frame.pack(fill="x", padx=10, pady=5)
    
    def _create_mode_selector(self, parent):
        """Create execution mode selection frame"""
        frame = ttk.LabelFrame(parent, text="執行模式", padding="10")
        frame.pack(fill="x", padx=10, pady=5)
        
        self.repeat_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(frame, text="重複執行", variable=self.repeat_var, value=True).pack(side="left", padx=20)
        ttk.Radiobutton(frame, text="單次執行", variable=self.repeat_var, value=False).pack(side="left", padx=20)
    
    def _create_control_buttons(self, parent):
        """Create control buttons frame"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=10, pady=10)
        
        buttons = [
            ("設定關機", self._schedule_shutdown),
            ("取消關機", self._cancel_shutdown),
            ("檢查排程", self._check_schedule)
        ]
        
        for text, command in buttons:
            ttk.Button(frame, text=text, command=command).pack(side="left", padx=5)
    
    def _create_status_display(self, parent):
        """Create status display label"""
        self.status_var = tk.StringVar(value="未設定關機排程")
        self.status_label = ttk.Label(
            parent,
            textvariable=self.status_var,
            wraplength=400,
            justify="left"
        )
        self.status_label.pack(pady=10, padx=10, fill="x")
    
    def _create_help_section(self, parent):
        """Create help section frame"""
        frame = ttk.LabelFrame(parent, text="使用說明", padding="10")
        frame.pack(fill="x", padx=10, pady=5)
        
        tips = [
            "1. 選擇要執行的星期（可複選）",
            "2. 設定執行時間（可選擇12或24小時制）",
            "3. 選擇執行模式（重複或單次）",
            "4. 系統會在關機前1分鐘顯示提醒",
            "5. 設定會自動保存，重開機後依然有效"
        ]
        
        for tip in tips:
            ttk.Label(frame, text=tip, wraplength=400).pack(anchor="w", pady=2)
            
    def _schedule_shutdown(self):
        """Schedule system shutdown"""
        try:
            # Get time
            time_str = self.time_frame.get_time_24h()
            if not time_str:
                return
            
            # Get selected weekdays
            selected_days = [i+1 for i, var in enumerate(self.weekday_vars) if var.get()]
            if not selected_days:
                raise ValueError("請至少選擇一個星期")
            
            # Create schedule
            is_repeat = self.repeat_var.get()
            self.scheduler.create_schedule(selected_days, time_str, is_repeat)
            
            # Update status
            self._update_status()
            messagebox.showinfo("成功", "已成功設定關機排程")
            
        except Exception as e:
            logger.error(f"Failed to schedule shutdown: {str(e)}")
            messagebox.showerror("錯誤", str(e))
    
    def _cancel_shutdown(self):
        """Cancel scheduled shutdown"""
        try:
            self.scheduler.remove_schedule()
            self.status_var.set("已取消關機排程")
            messagebox.showinfo("成功", "已取消關機排程")
        except Exception as e:
            logger.error(f"Failed to cancel shutdown: {str(e)}")
            messagebox.showerror("錯誤", str(e))
    
    def _check_schedule(self):
        """Check current schedule status"""
        try:
            task_info = self.scheduler.get_schedule_info()
            if task_info:
                self.status_var.set(task_info)
        except Exception as e:
            logger.error(f"Failed to check schedule: {str(e)}")
            messagebox.showerror("錯誤", str(e))
    
    def _load_saved_config(self):
        """Load saved configuration"""
        config = self.scheduler.load_config()
        if not config:
            return
        
        try:
            # Set weekday checkboxes
            saved_weekdays = config.get("weekdays", [])
            # saved_weekdays may be a list of booleans or a list of day numbers (1-7)
            if all(isinstance(x, bool) for x in saved_weekdays):
                for var, enabled in zip(self.weekday_vars, saved_weekdays):
                    var.set(enabled)
            else:
                # interpret numeric days
                try:
                    days = [int(x) for x in saved_weekdays]
                    for i, var in enumerate(self.weekday_vars):
                        var.set((i+1) in days)
                except Exception:
                    logger.debug("Unexpected format for saved weekdays, ignoring")
            
            # Set time
            time_str = config.get("time")
            time_format = config.get("time_format", "24")
            if time_str:
                self.time_frame.set_time(time_str, time_format)
            
            # Set execution mode
            self.repeat_var.set(config.get("is_repeat", True))
            
            # Update status
            self._update_status()
            
        except Exception:
            logger.exception("Failed to load configuration")
    
    def _update_status(self):
        """Update status display"""
        weekdays = [self.weekday_names[i] for i, var in enumerate(self.weekday_vars) if var.get()]
        weekdays_str = "、".join(weekdays)
        mode_str = "重複" if self.repeat_var.get() else "單次"
        time_str = self.time_frame.get_time_24h()
        
        status = [
            "目前設定：",
            f"執行模式：{mode_str}執行",
            f"執行時間：{time_str} ({self.time_frame.format_var.get()}小時制)",
            f"執行星期：{weekdays_str}"
        ]
        
        self.status_var.set("\n".join(status))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()