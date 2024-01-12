from PySide6.QtWidgets import QApplication

from ui.app import AppModel, AppView
from util.enums import FirstTabIndex
from util.init_app_manager import InitAppManager


class AppWidget:
    def __init__(self, parent=None):
        self._model = AppModel()
        self._view = AppView(parent)
        self.init_app_manager = InitAppManager()

        self.view.ui_initialized_signal.connect(self.init_controller)
        self.view.init_ui()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def init_controller(self):
        self.view.info_bar.view.btn_setting.clicked.connect(lambda: self.set_first_tab(FirstTabIndex.SETTING))
        self.view.tabs.view.first_tab.view.setting.view.btn.clicked.connect(self.set_home)
        self.view.tabs.view.first_tab.view.setting.view.btn_logout.clicked.connect(self.do_logout)
        self.view.tabs.view.first_tab.view.login.set_home_signal.connect(self.set_home)

        self.set_home()

    def set_home(self):
        # def get_first_tab_index_handler(index):
        #     # first_widget_index = reply
        #     self.set_first_tab(index)

        self.init_app_manager.get_first_tab_index(lambda index: self.set_first_tab(index))

    def set_first_tab(self, index):
        print(f"set_first_tab: {index}")
        self.view.tabs.set_first_tab(index)

    def do_logout(self):
        self.init_app_manager.logout()
        self.set_home()


def main():
    app = QApplication([])
    widget = AppWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
