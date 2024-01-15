from ui.app.main_tab.model import MainTabModel
from ui.app.main_tab.view import MainTabView
from ui.common.base_controller import BaseController


class MainTabController(BaseController):
    def __init__(self, parent=None):
        super().__init__(MainTabModel, MainTabView, parent)

    def set_first_tab(self, index):
        self.view.setCurrentIndex(0)
        self.view.first.set_current_index(index)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MainTabController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
