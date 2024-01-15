from ui.common.base_controller import BaseController
from ui.tabs.first_tab.home import HomeModel, HomeView


class HomeController(BaseController):
    def __init__(self, parent=None):
        super().__init__(HomeModel, HomeView, parent)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = HomeController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
