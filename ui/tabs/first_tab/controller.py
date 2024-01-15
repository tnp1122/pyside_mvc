from ui.common.base_controller import BaseController
from ui.tabs.first_tab import FirstTabModel, FirstTabView


class FirstTabController(BaseController):
    def __init__(self, parent=None):
        super().__init__(FirstTabModel, FirstTabView, parent)

    def set_current_index(self, index):
        self.view.setCurrentIndex(index.value)
        self.model.current_index = index

    def get_current_index(self):
        return self.model.current_index


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = FirstTabController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
