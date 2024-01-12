from PySide6.QtWidgets import QApplication

from ui.app.main_tab.model import MainTabModel
from ui.app.main_tab.view import MainTabView


class MainTabWidget:
    def __init__(self, parent=None):
        self._model = MainTabModel()
        self._view = MainTabView(parent)

        self.view.ui_initialized_signal.connect(self.init_controller)
        self.view.init_ui()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def init_controller(self):
        pass

    def set_first_tab(self, index):
        self.view.setCurrentIndex(0)
        self.view.first.set_current_index(index)


def main():
    app = QApplication([])
    widget = MainTabWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
