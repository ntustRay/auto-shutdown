"""Main entry point for the auto shutdown application"""
import logging
from pathlib import Path
from src.config import LOG_FILE_NAME


def main():
    """Application entry point"""
    # Configure logging centrally so importing modules won't
    # reconfigure handlers or write files unexpectedly.
    log_path = Path.cwd() / LOG_FILE_NAME
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # Import UI after logging is configured so modules can use logging.getLogger
    from src.ui.main_window import AutoShutdownWindow

    try:
        app = AutoShutdownWindow()
        app.run()
    except Exception:
        logging.getLogger(__name__).exception("Application error")
        raise


if __name__ == "__main__":
    main()