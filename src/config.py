"""
自動關機應用程式設定常數
"""

# 視窗尺寸
WINDOW_WIDTH = 420
WINDOW_HEIGHT = 750
WINDOW_RESIZABLE = False

# 預設時間
DEFAULT_HOUR = "23"
DEFAULT_MINUTE = "28"
DEFAULT_TIME_FORMAT = "24小時"
DEFAULT_REPEAT = True

# UI尺寸
BUTTON_HEIGHT_LARGE = 48
BUTTON_HEIGHT_MEDIUM = 40
BUTTON_HEIGHT_SMALL = 28
TIME_CANVAS_HEIGHT = 200
REPEAT_CANVAS_HEIGHT = 72
HELP_CANVAS_COLLAPSED = 50
HELP_CANVAS_EXPANDED = 130

# 版面間距
PADDING_MAIN = 16
PADDING_SECTION = 20
PADDING_WIDGET = 12
CORNER_RADIUS = 16

# 動畫時間設定
COLON_BLINK_INTERVAL = 500  # milliseconds
SHUTDOWN_WARNING_TIME = 60  # seconds

# 檔案路徑
CONFIG_FILE_NAME = ".auto_shutdown_config.json"
LOG_FILE_NAME = "auto_shutdown.log"
TASK_NAME = "AutomaticShutdownScheduler"

# Windows工作排程器的日期對應
DAY_MAPPING = {
    1: "MON", 2: "TUE", 3: "WED", 4: "THU",
    5: "FRI", 6: "SAT", 7: "SUN"
}

# 中文的星期名稱
WEEKDAY_NAMES = ["一", "二", "三", "四", "五", "六", "日"]
WEEKDAY_FULL_NAMES = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# 預設選中的星期（一和五）
DEFAULT_SELECTED_DAYS = {0, 4}

# 訊息字串
MESSAGES = {
    "validation_error": "請至少選擇一個星期",
    "permission_error": "需要管理員權限才能建立排程任務。\n請以系統管理員身份運行程式。",
    "success_scheduled": "已成功設定關機排程",
    "success_canceled": "已取消關機排程",
    "error_title": "錯誤",
    "input_error": "輸入錯誤",
    "success_title": "成功",
    "schedule_status": "排程狀態",
    "active_status": "已設定排程",
    "inactive_status": "未設定排程"
}

# 說明提示
HELP_TIPS = [
    "• 選擇要執行的星期 (可複選)",
    "• 系統會在關機前1分鐘顯示提醒",
    "• 設定會自動保存，重開機後依然有效"
]

# 子程式命令
SHUTDOWN_COMMAND = "shutdown /s /t 60 /c \"系統將在1分鐘後關機\""

# 編碼設定
SUBPROCESS_ENCODING = "cp950"  # 適用於Windows中文系統
CONFIG_ENCODING = "utf-8"
