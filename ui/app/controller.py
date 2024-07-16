import json

from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.app import AppModel, AppView
from ui.common import BaseController
from util.enums import FirstTabIndex
from util.init_app_manager import InitAppManager
from util.setting_manager import SettingManager


class AppController(BaseController):
    def __init__(self, parent=None):
        self.init_app_manager = InitAppManager()
        self.api_manager = APIManager()
        self.setting_manager = SettingManager()
        super().__init__(AppModel, AppView, parent)

    def init_controller(self):
        super().init_controller()

        view: AppView = self.view

        view.setMinimumSize(1280, 840)
        view.info_bar.view.btn_setting.clicked.connect(self.show_setting_widget)
        view.tabs.view.first.view.setting.view.btn_home.clicked.connect(self.show_first_widget)
        view.tabs.view.first.view.setting.view.btn_logout.clicked.connect(self.do_logout)
        view.tabs.view.first.view.login.set_home_signal.connect(self.update_user_info)
        view.tabs.view.currentChanged.connect(self.tab_switched_handler)

        self.update_user_info()

    def update_user_info(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                data = reply.readAll().data().decode("utf-8")
                user_info = json.loads(data)["user_info"]
                self.model.username = user_info["username"]
                self.model.name = user_info["name"]
                self.model.role = user_info["role"]

                self.model.first_tab_index = FirstTabIndex.HOME
                self.setting_manager.set_experimenter_name(self.model.name)
            else:
                self.model.username = ""
                self.model.name = "사용자"
                self.model.role = ""
                self.model.first_tab_index = FirstTabIndex.LOGIN

            is_admin = self.model.role == "admin"
            self.view.tabs.view.set_admin_tab(is_admin)
            self.view.info_bar.view.lb_name.setText(self.model.name)
            self.set_first_tab()

        self.api_manager.get_user_info(callback=api_handler)

    def tab_switched_handler(self, index):
        if index == 0:
            self.show_first_widget(switch=False)

    def show_first_widget(self, switch=True):
        self.model.first_tab_index = FirstTabIndex.LOGIN
        if self.setting_manager.get_access_token():
            if self.model.username:
                self.model.first_tab_index = FirstTabIndex.HOME

        self.set_first_tab(switch=switch)

    def show_setting_widget(self):
        self.model.first_tab_index = FirstTabIndex.SETTING
        self.set_first_tab()

    def set_first_tab(self, switch=True):
        self.view.tabs.set_first_tab(self.model.first_tab_index, switch)

    def do_logout(self):
        self.model.username, self.model.name, self.model.role = "", "", ""
        self.init_app_manager.logout()
        self.update_user_info()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AppController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
