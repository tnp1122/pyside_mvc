import logging

from PySide6.QtCore import Signal
from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.common.base_controller import BaseController
from ui.tabs.first_tab.login import LoginModel, LoginView
from util.setting_manager import SettingManager

METHOD = "[Login Controller]"
USERNAME_L = 0
PASSWORD_L = 1
USERNAME_R = 2
PASSWORD_R = 3
NAME = 4


class LoginWidget(BaseController):
    set_home_signal = Signal()

    api_manager = APIManager()
    setting_manager = SettingManager()

    def __init__(self, parent=None):
        super().__init__(LoginModel, LoginView, parent)

    def init_controller(self):
        super().init_controller()

        self.view.et_username_login.textChanged.connect(lambda value: self.on_text_changed(value, USERNAME_L))
        self.view.et_password_login.textChanged.connect(lambda value: self.on_text_changed(value, PASSWORD_L))
        self.view.et_username_rg.textChanged.connect(lambda value: self.on_text_changed(value, USERNAME_R))
        self.view.et_password_rg.textChanged.connect(lambda value: self.on_text_changed(value, PASSWORD_R))
        self.view.et_name.textChanged.connect(lambda value: self.on_text_changed(value, NAME))

        self.view.btn_login.clicked.connect(self.login)
        self.view.btn_rg.clicked.connect(self.regist)

    def on_text_changed(self, value, index):
        if index == USERNAME_L:
            self.model.username_login = value
        elif index == PASSWORD_L:
            self.model.password_login = value
        elif index == USERNAME_R:
            self.model.username_rg = value
        elif index == PASSWORD_R:
            self.model.password_rg = value
        else:
            self.model.name = value

    def login(self):
        username = self.model.username_login
        password = self.model.password_login

        login_info = {"username": username, "password": password}

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                data = reply.readAll().data().decode("utf-8")
                print(f"응답 성공\ndata:", data)
                headers = reply.rawHeaderPairs()
                tokens = ""
                for header, value in headers:
                    if header == b"Authorization":
                        auth = value.data().decode("utf-8")
                        tokens = auth.split(" ")[1].split("/")

                print("refresh:", tokens[0])
                print("access:", tokens[1])
                self.setting_manager.set_refresh_token(tokens[0])
                self.setting_manager.set_access_token(tokens[1])
                self.set_home_signal.emit()

            else:
                logging.error(f"{METHOD} login-{reply.errorString()}")

        self.api_manager.login(login_info, api_handler)

    def regist(self):
        name = self.model.name
        username = self.model.username_rg
        password = self.model.password_rg

        registration_info = {"name": name, "username": username, "password": password}

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                data = reply.readAll().data().decode("utf-8")
                print(f"응답 성공\ndata:", data)
                headers = reply.rawHeaderPairs()
                for header in headers:
                    print(f"Header: {header[0]} = {header[1].data().decode('utf-8')}")

            else:
                logging.error(f"{METHOD} regist-{reply.errorString()}")

        self.api_manager.regist(registration_info, api_handler)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = LoginWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
