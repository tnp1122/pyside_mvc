import logging
import os
import sys
from datetime import datetime


def logging_config():
    current_directory = os.getcwd()
    log_folder_path = os.path.join(current_directory, "log")
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path)

    now = datetime.now()
    now_str = now.strftime("%y%m%d_%H%M%S")
    file_name = os.path.join(log_folder_path, now_str)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def exception_hook(exc_type, exc_value, exc_traceback):
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


def main():
    from dotenv import load_dotenv

    from PySide6.QtWidgets import QApplication
    from ui.app import AppController

    load_dotenv()
    app = QApplication([])
    main_app = AppController()
    main_app.view.show()
    app.exec()


if __name__ == "__main__":
    logging_config()
    sys.excepthook = exception_hook
    main()
