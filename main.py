def main():
    from dotenv import load_dotenv
    import os
    import logging

    from PySide6.QtWidgets import QApplication
    from ui.app import AppController

    load_dotenv()
    file_name = os.getenv("LOG_FILE_NAME")

    if file_name:
        logging.basicConfig(filename=file_name, filemode="w")
    else:
        logging.basicConfig(
            format='[%(levelname)s] %(asctime)s:%(message)s',
            datefmt='%Y-%m-%d %I:%M:%S %p',
            level=logging.DEBUG
        )
    app = QApplication([])
    main_app = AppController()
    main_app.view.show()
    app.exec()


if __name__ == "__main__":
    main()
