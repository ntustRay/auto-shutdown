"""Unified scheduler module for handling system shutdown scheduling"""
import json
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
import logging

# Note: logging configuration is moved to the application entry point (main.py)
# so importing this module doesn't configure global logging handlers.
logger = logging.getLogger(__name__)

# Common schtasks subcommand used in multiple places
SCHTASKS_QUERY = "/query"

class ShutdownScheduler:
    """Unified scheduler class for managing system shutdown tasks"""
    
    def __init__(self):
        self.config_path = Path.home() / ".auto_shutdown_config.json"
        self.system = platform.system()
        self.task_name = "AutomaticShutdownScheduler"
        # 用於檢查的任務名稱列表（包括舊版本使用的名稱）
        self.possible_task_names = [
            "AutomaticShutdownScheduler",
            "AutomaticS",  # 可能的簡短版本
            "AutoShutdown"  # 舊版本使用的名稱
        ]
        
        # Mapping for day numbers to different system formats
        self.day_mapping = {
            "Windows": {
                1: "MON", 2: "TUE", 3: "WED", 4: "THU",
                5: "FRI", 6: "SAT", 7: "SUN"
            },
            "Unix": {
                1: "1", 2: "2", 3: "3", 4: "4",
                5: "5", 6: "6", 7: "7"
            }
        }
    
    def create_schedule(self, weekdays, time, is_repeat):
        """Create a system shutdown schedule"""
        try:
            if self.system == "Windows":
                self._create_windows_task(weekdays, time, is_repeat)
            else:
                self._create_unix_cron(weekdays, time, is_repeat)
            
            self._save_config({
                "weekdays": weekdays,
                "time": time,
                "is_repeat": is_repeat,
                "created_at": datetime.now().isoformat()
            })
            logger.info(f"Successfully created schedule for {time} on days {weekdays}")
            
        except Exception as e:
            logger.error(f"Failed to create schedule: {str(e)}")
            raise
    
    def remove_schedule(self):
        """Remove existing shutdown schedule"""
        try:
            if self.system == "Windows":
                subprocess.run(
                    ["schtasks", "/delete", "/tn", self.task_name, "/f"],
                    capture_output=True,
                    check=True
                )
            else:
                self._remove_cron_task()
            
            if self.config_path.exists():
                self.config_path.unlink()
            
            logger.info("Successfully removed schedule")
            
        except Exception as e:
            logger.error(f"Failed to remove schedule: {str(e)}")
            raise
    
    def get_schedule_info(self):
        """Get current schedule information"""
        try:
            if self.system == "Windows":
                return self._get_windows_task_info()
            return self._get_unix_task_info()
        except Exception as e:
            logger.error(f"Failed to get schedule info: {str(e)}")
            return "無法獲取排程資訊"
    
    def load_config(self):
        """Load saved configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return None
    
    def _save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            raise
    
    def _create_windows_task(self, weekdays, time, _is_repeat):
        """Create Windows scheduled task"""
        hour, minute = map(int, time.split(":"))
        weekdays_str = " ".join(self.day_mapping["Windows"][day] for day in weekdays)
        
        # 先刪除可能存在的舊任務
        try:
            subprocess.run(
                ["schtasks", "/delete", "/tn", self.task_name, "/f"],
                capture_output=True,
                text=True,
                encoding='cp950'
            )
        except Exception:
            # ignore delete errors
            pass
            
        # 建立新任務，使用更完整的命令參數
        cmd = [
            "schtasks", "/create",
            "/tn", self.task_name,
            "/tr", "shutdown /s /t 60 /c \"系統將在1分鐘後關機\"",
            "/sc", "WEEKLY",
            "/d", weekdays_str,
            "/st", f"{hour:02d}:{minute:02d}",
            "/ru", "SYSTEM",
            "/f",
            "/rl", "HIGHEST"  # 使用最高權限運行
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='cp950'
            )
            
            if result.returncode == 0:
                logger.info("Windows task created successfully")
                # 驗證任務是否確實創建
                verify_result = subprocess.run(
                    ["schtasks", SCHTASKS_QUERY, "/tn", self.task_name],
                    capture_output=True,
                    text=True,
                    encoding='cp950'
                )
                
                if verify_result.returncode == 0:
                    logger.info("Task verified successfully")
                    return result
                else:
                    raise RuntimeError("任務創建後無法驗證")
            else:
                raise RuntimeError("創建任務失敗: " + result.stderr)
                
        except Exception as e:
            logger.error(f"Failed to create Windows task: {str(e)}")
            raise
    
    def _create_unix_cron(self, weekdays, time, is_repeat):
        """Create Unix/Linux crontab schedule"""
        hour, minute = map(int, time.split(":"))
        days = ",".join(self.day_mapping["Unix"][day] for day in weekdays)
        cron_time = f"{minute} {hour} * * {days}"
        
        try:
            current_crontab = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                check=True
            ).stdout
            
            # Remove existing shutdown tasks
            crontab_lines = [line for line in current_crontab.splitlines()
                           if "shutdown -h now" not in line]
            
            if is_repeat:
                crontab_lines.append(f"{cron_time} shutdown -h now")
            
            new_crontab = "\n".join(crontab_lines) + "\n"
            subprocess.run(
                ["crontab", "-"],
                input=new_crontab,
                text=True,
                check=True
            )
            logger.info("Unix crontab updated successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update crontab: {str(e)}")
            raise
    
    def _get_windows_task_info(self):
        """Get Windows task information"""
        task_info = None
        error_messages = []

        try:
            # 首先列出所有任務
            list_result = subprocess.run(
                ["schtasks", SCHTASKS_QUERY, "/fo", "csv", "/nh"],
                capture_output=True,
                text=True,
                encoding='cp950'
            )
            
            if list_result.returncode == 0:
                tasks = list_result.stdout.splitlines()
                for task in tasks:
                    # CSV 格式，第一個欄位是任務名稱
                    if ',' in task:
                        current_task_name = task.split(',')[0].strip('"')
                        if "AutomaticShutdownScheduler" in current_task_name:
                            logger.info(f"Found task: {current_task_name}")
                            # 獲取詳細資訊
                            detail_result = subprocess.run(
                                ["schtasks", SCHTASKS_QUERY, "/tn", current_task_name, "/v", "/fo", "list"],
                                capture_output=True,
                                text=True,
                                encoding='cp950'
                            )
                            
                            if detail_result.returncode == 0:
                                # 解析詳細資訊
                                current_info = {}
                                for line in detail_result.stdout.split('\n'):
                                    if ': ' in line:
                                        key, value = line.split(': ', 1)
                                        current_info[key.strip()] = value.strip()
                                
                                if current_info:
                                    task_info = current_info
                                    self.task_name = current_task_name
                                    break
        
        except Exception as e:
            error_messages.append(f"檢查任務時發生錯誤: {str(e)}")
            logger.error(f"Error checking tasks: {str(e)}")
                
        # 如果找到任務信息
        if task_info:
            logger.info(f"Found task info: {task_info}")
            return self._format_task_info(task_info)
            
        # 如果沒有找到任何任務，嘗試使用 wmic
        try:
            wmic_result = subprocess.run(
                ["wmic", "job", "list", "full"],
                capture_output=True,
                text=True,
                encoding='cp950'
            )
            
            if wmic_result.returncode == 0:
                if "AutomaticShutdownScheduler" in wmic_result.stdout:
                    return "找到排程任務，但無法取得詳細資訊。建議使用系統管理員權限執行。"
        except Exception:
            pass
            
        # 如果有錯誤訊息
        if error_messages:
            logger.warning("Errors while checking tasks: " + "\n".join(error_messages))
            return "檢查任務時發生錯誤，請以系統管理員身份運行程式"
            
        logger.warning("No shutdown task found")
        return "找不到排程任務"

    
    def _get_unix_task_info(self):
        """Get Unix crontab task information"""
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                check=True
            )
            
            cron_lines = [line for line in result.stdout.splitlines()
                         if "shutdown -h now" in line]
            
            if not cron_lines:
                return "找不到排程任務"
            
            return "目前的 crontab 排程：\n" + "\n".join(cron_lines)
            
        except subprocess.CalledProcessError:
            return "無法讀取 crontab"
    
    def _format_task_info(self, task_info):
        """Format task information for display"""
        # 嘗試不同的可能的鍵名（中文系統可能有不同翻譯）
        name_keys = ['工作名稱', 'TaskName', '名稱']
        next_run_keys = ['下次執行時間', 'Next Run Time', '下次運行時間']
        schedule_type_keys = ['排程類型', 'Schedule Type', '類型']
        last_run_keys = ['上次執行時間', 'Last Run Time', '上次運行時間']
        last_result_keys = ['上次執行的結果', 'Last Result', '最後結果']
        account_keys = ['執行身分', 'Run As User', '運行身分']
        
        def get_first_match(keys):
            return next((task_info.get(k) for k in keys if k in task_info), '未知')
        
        return f"""排程狀態：
任務名稱: {get_first_match(name_keys)}
下次執行時間: {get_first_match(next_run_keys)}
排程類型: {get_first_match(schedule_type_keys)}
上次執行時間: {get_first_match(last_run_keys)}
上次執行結果: {get_first_match(last_result_keys)}
執行身分: {get_first_match(account_keys)}
"""