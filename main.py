"""自動關機應用程式主入口點"""
import logging
from pathlib import Path
from src.config import LOG_FILE_NAME


def main():
    """應用程式入口點"""
    # 集中設定日誌記錄，避免匯入模組時
    # 重新設定處理器或意外寫入檔案。
    log_path = Path.cwd() / LOG_FILE_NAME
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # 在日誌設定完成後匯入UI，讓模組可以使用logging.getLogger
    from src.ui.main_window import AutoShutdownWindow

    try:
        app = AutoShutdownWindow()
        app.run()
    except Exception:
        logging.getLogger(__name__).exception("Application error")
        raise


if __name__ == "__main__":
    main()