from ui.app.main_tab import MainTabModel, MainTabView
from ui.common import BaseController


class MainTabController(BaseController):
    initialized_tabs = [0]
    tab_count = 0

    def __init__(self, parent=None):
        super().__init__(MainTabModel, MainTabView, parent)

    def init_controller(self):
        super().init_controller()

        self.view.currentChanged.connect(self.check_tab)
        self.tab_count = self.view.count()

    def set_first_tab(self, index, switch=True):
        if switch:
            self.view.setCurrentIndex(0)
        self.view.first.set_current_index(index)

    def check_tab(self, index):
        if index not in self.initialized_tabs:
            self.view.widget(index).late_init()
            self.initialized_tabs.append(index)

        if self.tab_count == len(self.initialized_tabs):
            self.view.currentChanged.disconnect()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MainTabController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
