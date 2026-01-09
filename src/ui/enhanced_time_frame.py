"""Custom time selection frame with 12/24 hour format support"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class EnhancedTimeFrame(ttk.LabelFrame):
    """Enhanced time selection frame with format switching and validation"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_variables()
        self._create_widgets()
        self._setup_bindings()
    
    def _setup_variables(self):
        """Initialize tkinter variables"""
        self.format_var = tk.StringVar(value="24")
        self.hour_var = tk.StringVar()
        self.minute_var = tk.StringVar()
        self.ampm_var = tk.StringVar(value="AM")
    
    def _create_widgets(self):
        """Create and arrange widgets"""
        self._create_format_selector()
        self._create_time_selector()
    
    def _create_format_selector(self):
        """Create time format selection radio buttons"""
        format_frame = ttk.Frame(self)
        format_frame.pack(fill="x", padx=5, pady=5)
        
        for text, value in [("24小時制", "24"), ("12小時制", "12")]:
            ttk.Radiobutton(
                format_frame,
                text=text,
                variable=self.format_var,
                value=value,
                command=self._update_time_format
            ).pack(side="left", padx=10)
    
    def _create_time_selector(self):
        """Create time selection widgets"""
        time_frame = ttk.Frame(self)
        time_frame.pack(fill="x", padx=5, pady=5)
        
        # Hour selector
        ttk.Label(time_frame, text="時:").pack(side="left")
        self.hour_combo = ttk.Combobox(
            time_frame,
            textvariable=self.hour_var,
            width=5,
            state="readonly"
        )
        self.hour_combo.pack(side="left", padx=5)
        
        # Minute selector
        ttk.Label(time_frame, text="分:").pack(side="left")
        self.minute_combo = ttk.Combobox(
            time_frame,
            textvariable=self.minute_var,
            width=5,
            state="readonly",
            values=[f"{i:02d}" for i in range(60)]
        )
        self.minute_combo.pack(side="left", padx=5)
        
        # AM/PM selector
        self.ampm_combo = ttk.Combobox(
            time_frame,
            textvariable=self.ampm_var,
            width=5,
            state="readonly",
            values=["AM", "PM"]
        )
        self.ampm_combo.pack(side="left", padx=5)
        
        self._update_time_format()
        self.set_current_time()
    
    def _setup_bindings(self):
        """Setup widget event bindings"""
        for widget in (self.hour_combo, self.minute_combo, self.ampm_combo):
            widget.bind('<<ComboboxSelected>>', self._validate_time)
    
    def _update_time_format(self):
        """Update time format and hour options"""
        is_24h = self.format_var.get() == "24"
        
        self.hour_combo['values'] = [
            f"{i:02d}" for i in range(24 if is_24h else 1, 13)
        ]
        
        if is_24h:
            self.ampm_combo.pack_forget()
        else:
            self.ampm_combo.pack(side="left", padx=5)
        
        self.set_current_time()
    
    def set_current_time(self):
        """Set current time in the selectors"""
        now = datetime.now()
        hour = now.hour
        
        if self.format_var.get() == "12":
            self.ampm_var.set("PM" if hour >= 12 else "AM")
            hour = hour % 12
            hour = 12 if hour == 0 else hour
        
        self.hour_var.set(f"{hour:02d}")
        self.minute_var.set(f"{now.minute:02d}")
    
    def _validate_time(self, event=None):
        """Validate time input"""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            
            if self.format_var.get() == "12":
                if self.ampm_var.get() == "PM" and hour != 12:
                    hour += 12
                elif self.ampm_var.get() == "AM" and hour == 12:
                    hour = 0
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            
            return True
            
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的時間")
            return False
    
    def get_time_24h(self):
        """Get time in 24-hour format"""
        if not self._validate_time():
            return None
        
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        
        if self.format_var.get() == "12":
            if self.ampm_var.get() == "PM" and hour != 12:
                hour += 12
            elif self.ampm_var.get() == "AM" and hour == 12:
                hour = 0
        
        return f"{hour:02d}:{minute:02d}"
    
    def set_time(self, time_str, time_format="24"):
        """Set time from string"""
        try:
            hour, minute = map(int, time_str.split(":"))
            self.format_var.set(time_format)
            self._update_time_format()
            
            if time_format == "12":
                ampm = "PM" if hour >= 12 else "AM"
                if hour > 12:
                    hour -= 12
                elif hour == 0:
                    hour = 12
                self.ampm_var.set(ampm)
            
            self.hour_var.set(f"{hour:02d}")
            self.minute_var.set(f"{minute:02d}")
            
        except (ValueError, TypeError):
            self.set_current_time()