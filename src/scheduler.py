"""Windows專用排程模組，處理系統關機排程"""

import csv
import json
import locale
import subprocess
from datetime import datetime
from pathlib import Path
import logging

from .config import (
    CONFIG_FILE_NAME,
    TASK_NAME,
    DAY_MAPPING,
    SHUTDOWN_COMMAND,
    CONFIG_ENCODING,
    SUBPROCESS_ENCODING,
)

logger = logging.getLogger(__name__)

# 在多處使用的通用schtasks子命令
SCHTASKS_QUERY = "/query"


class ShutdownScheduler:
    """Windows排程器類別，用於管理系統關機任務"""

    def __init__(self):
        self.config_path = Path.home() / CONFIG_FILE_NAME
        self.task_name = TASK_NAME
        # 要檢查的任務名稱列表（包括舊版本使用的名稱）
        self.possible_task_names = [
            TASK_NAME,
            "AutomaticS",  # 可能的簡短版本
            "AutoShutdown",  # 舊版本使用的名稱
        ]
        # 使用配置中的編碼設定
        self.encoding = SUBPROCESS_ENCODING

    def create_schedule(self, weekdays, time, is_repeat):
        """建立系統關機排程"""
        # 驗證輸入
        for day in weekdays:
            if day not in DAY_MAPPING:
                raise ValueError(f"無效的星期: {day} (必須是 1-7)")

        try:
            self._create_windows_task(weekdays, time)

            self._save_config(
                {
                    "weekdays": weekdays,
                    "time": time,
                    "is_repeat": is_repeat,
                    "created_at": datetime.now().isoformat(),
                }
            )
            logger.info(f"Successfully created schedule for {time} on days {weekdays}")

        except Exception as e:
            logger.error(f"Failed to create schedule: {str(e)}")
            raise

    def remove_schedule(self):
        """移除現有關機排程"""
        try:
            subprocess.run(
                ["schtasks", "/delete", "/tn", self.task_name, "/f"],
                capture_output=True,
                check=True,
            )

            if self.config_path.exists():
                try:
                    self.config_path.unlink()
                    logger.info("Configuration file removed successfully")
                except Exception as e:
                    logger.warning(f"Failed to remove config file: {str(e)}")
                    # 不要拋出異常，因為主要任務是移除系統排程

            logger.info("Successfully removed schedule")

        except Exception as e:
            logger.error(f"Failed to remove schedule: {str(e)}")
            raise

    def get_schedule_info(self):
        """取得目前排程資訊"""
        try:
            return self._get_windows_task_info()
        except Exception as e:
            logger.error(f"Failed to get schedule info: {str(e)}")
            return "無法獲取排程資訊"

    def load_config(self):
        """載入已儲存的設定"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding=CONFIG_ENCODING) as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return None

    def _save_config(self, config):
        """將設定儲存到檔案"""
        try:
            with open(self.config_path, "w", encoding=CONFIG_ENCODING) as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            raise

    def _create_windows_task(self, weekdays, time):
        """建立Windows排程任務"""
        hour, minute = map(int, time.split(":"))
        weekdays_str = " ".join(DAY_MAPPING[day] for day in weekdays)

        # 刪除任何現有的舊任務
        try:
            subprocess.run(
                ["schtasks", "/delete", "/tn", self.task_name, "/f"],
                capture_output=True,
                text=True,
                encoding=SUBPROCESS_ENCODING,
            )
        except Exception as e:
            logger.warning(f"Failed to delete existing task, continuing: {str(e)}")

        # 使用完整命令參數建立新任務
        cmd = [
            "schtasks",
            "/create",
            "/tn",
            self.task_name,
            "/tr",
            SHUTDOWN_COMMAND,
            "/sc",
            "WEEKLY",
            "/d",
            weekdays_str,
            "/st",
            f"{hour:02d}:{minute:02d}",
            "/ru",
            "SYSTEM",
            "/f",
            "/rl",
            "HIGHEST",  # 以最高權限執行
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding=SUBPROCESS_ENCODING
            )

            if result.returncode == 0:
                logger.info("Windows task created successfully")
                # 驗證任務是否實際建立
                verify_result = subprocess.run(
                    ["schtasks", SCHTASKS_QUERY, "/tn", self.task_name],
                    capture_output=True,
                    text=True,
                    encoding=SUBPROCESS_ENCODING,
                )

                if verify_result.returncode == 0:
                    logger.info("Task verified successfully")
                    return result
                else:
                    raise RuntimeError("Task verification failed after creation")
            else:
                raise RuntimeError("Task creation failed: " + result.stderr)

        except Exception as e:
            logger.error(f"Failed to create Windows task: {str(e)}")
            raise

    def _get_windows_task_info(self):
        """取得Windows任務資訊"""
        task_info = None
        error_messages = []

        try:
            # 首先列出所有任務
            list_result = subprocess.run(
                ["schtasks", SCHTASKS_QUERY, "/fo", "csv", "/nh"],
                capture_output=True,
                text=True,
                encoding=SUBPROCESS_ENCODING,
            )

            if list_result.returncode == 0:
                tasks = list_result.stdout.splitlines()
                for task in tasks:
                    # CSV格式，第一個欄位是任務名稱
                    if "," in task:
                        current_task_name = task.split(",")[0].strip('"')
                        # 移除可能的路徑前綴（例如 \AutomaticShutdownScheduler 或 TaskFolder\AutomaticShutdownScheduler）
                        # 使用 partition 來處理各種路徑格式
                        normalized_name = (
                            current_task_name.split("\\")[-1]
                            if "\\" in current_task_name
                            else current_task_name
                        )

                        # 檢查是否匹配（包含完整名稱和簡短版本）
                        is_match = (
                            normalized_name == TASK_NAME
                            or normalized_name in self.possible_task_names
                            or current_task_name == TASK_NAME
                            or current_task_name in self.possible_task_names
                        )

                        # 額外檢查：如果任務名稱包含我們的任務名稱作為後綴
                        if not is_match and TASK_NAME in current_task_name:
                            # 檢查最後一部分是否匹配
                            last_part = current_task_name.split("\\")[-1]
                            if (
                                last_part == TASK_NAME
                                or last_part in self.possible_task_names
                            ):
                                is_match = True

                        if is_match:
                            logger.info(f"Found task: {current_task_name}")
                            # 取得詳細資訊
                            detail_result = subprocess.run(
                                [
                                    "schtasks",
                                    SCHTASKS_QUERY,
                                    "/tn",
                                    current_task_name,
                                    "/v",
                                    "/fo",
                                    "list",
                                ],
                                capture_output=True,
                                text=True,
                                encoding=SUBPROCESS_ENCODING,
                            )

                            if detail_result.returncode == 0:
                                # 解析詳細資訊
                                current_info = {}
                                for line in detail_result.stdout.split("\n"):
                                    if ": " in line:
                                        key, value = line.split(": ", 1)
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

        # 如果找不到任務，嘗試使用 wmic
        try:
            wmic_result = subprocess.run(
                ["wmic", "job", "list", "full"],
                capture_output=True,
                text=True,
                encoding=SUBPROCESS_ENCODING,
            )

            if wmic_result.returncode == 0:
                if "AutomaticShutdownScheduler" in wmic_result.stdout:
                    return (
                        "找到排程任務，但無法取得詳細資訊。建議使用系統管理員權限執行。"
                    )
        except Exception:
            pass

        # 如果有錯誤訊息
        if error_messages:
            logger.warning("Errors while checking tasks: " + "\n".join(error_messages))
            return "檢查任務時發生錯誤，請以系統管理員身份運行程式"

        logger.warning("No shutdown task found")
        return "找不到排程任務"

    def _format_task_info(self, task_info):
        """格式化任務資訊以供顯示"""
        # 嘗試不同的可能的鍵名（中文系統可能有不同翻譯）
        name_keys = ["工作名稱", "TaskName", "名稱"]
        next_run_keys = ["下次執行時間", "Next Run Time", "下次運行時間"]
        schedule_type_keys = ["排程類型", "Schedule Type", "類型"]
        last_run_keys = ["上次執行時間", "Last Run Time", "上次運行時間"]
        last_result_keys = ["上次執行的結果", "Last Result", "最後結果"]
        account_keys = ["執行身分", "Run As User", "運行身分"]

        def get_first_match(keys):
            return next((task_info.get(k) for k in keys if k in task_info), "未知")

        return f"""排程狀態：
任務名稱: {get_first_match(name_keys)}
下次執行時間: {get_first_match(next_run_keys)}
排程類型: {get_first_match(schedule_type_keys)}
上次執行時間: {get_first_match(last_run_keys)}
上次執行結果: {get_first_match(last_result_keys)}
執行身分: {get_first_match(account_keys)}
"""

    def has_active_schedule(self):
        """檢查是否有執行中的排程"""
        try:
            # 同時檢查Windows任務排程器和配置檔案
            has_task = False
            has_config = self.config_path.exists()

            # 檢查Windows任務排程器
            list_result = subprocess.run(
                ["schtasks", SCHTASKS_QUERY, "/fo", "csv", "/nh"],
                capture_output=True,
                text=True,
                encoding=SUBPROCESS_ENCODING,
            )

            if list_result.returncode == 0:
                tasks = list_result.stdout.splitlines()
                for task in tasks:
                    # CSV格式，第一個欄位是任務名稱
                    if "," in task:
                        current_task_name = task.split(",")[0].strip('"')
                        # 移除可能的路徑前綴（例如 \AutomaticShutdownScheduler 或 TaskFolder\AutomaticShutdownScheduler）
                        normalized_name = (
                            current_task_name.split("\\")[-1]
                            if "\\" in current_task_name
                            else current_task_name
                        )

                        # 檢查是否匹配（包含完整名稱和簡短版本）
                        is_match = (
                            normalized_name == TASK_NAME
                            or normalized_name in self.possible_task_names
                            or current_task_name == TASK_NAME
                            or current_task_name in self.possible_task_names
                        )

                        # 額外檢查：如果任務名稱包含我們的任務名稱作為後綴
                        if not is_match and TASK_NAME in current_task_name:
                            # 檢查最後一部分是否匹配
                            last_part = current_task_name.split("\\")[-1]
                            if (
                                last_part == TASK_NAME
                                or last_part in self.possible_task_names
                            ):
                                is_match = True

                        if is_match:
                            logger.info(f"Found active schedule: {current_task_name}")
                            has_task = True
                            break

            # 只要Windows任務排程器中存在任務，就認為有活躍排程
            # 配置檔案遺失不應影響排程狀態的判定
            logger.info(
                f"has_active_schedule check - task: {has_task}, config: {has_config}"
            )
            return has_task
        except Exception as e:
            logger.error(f"Error checking active schedule: {str(e)}")
            return False
