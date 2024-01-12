from PySide6.QtWidgets import QApplication

from ui.app import AppWidget


def main():
    app = QApplication([])
    main_app = AppWidget()
    main_app.view.show()
    app.exec()


if __name__ == "__main__":
    main()
