def main():
    from PySide6.QtWidgets import QApplication
    from ui.app import AppController

    app = QApplication([])
    main_app = AppController()
    main_app.view.show()
    app.exec()


if __name__ == "__main__":
    main()
