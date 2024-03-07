import hashlib
import json
import logging

from PySide6.QtCore import Signal
from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.common.toast import Toast
from ui.common import BaseController
from ui.tabs.first_tab.login import LoginModel, LoginView
from util.setting_manager import SettingManager

METHOD = "[Login Controller]"
USERNAME_L = 0
PASSWORD_L = 1
USERNAME_R = 2
PASSWORD_R = 3
CONFIRM_PASSWORD = 4
NAME = 5


class LoginWidget(BaseController):
    set_home_signal = Signal()

    api_manager = APIManager()
    setting_manager = SettingManager()

    def __init__(self, parent=None):
        super().__init__(LoginModel, LoginView, parent)

    def init_controller(self):
        super().init_controller()

        view: LoginView = self.view

        view.et_username_login.textChanged.connect(lambda value: self.on_text_changed(value, USERNAME_L))
        view.et_password_login.textChanged.connect(lambda value: self.on_text_changed(value, PASSWORD_L))
        view.et_username_rg.textChanged.connect(lambda value: self.on_text_changed(value, USERNAME_R))
        view.et_password_rg.textChanged.connect(lambda value: self.on_text_changed(value, PASSWORD_R))
        view.et_confirm_password.textChanged.connect(lambda value: self.on_text_changed(value, CONFIRM_PASSWORD))
        view.et_name.textChanged.connect(lambda value: self.on_text_changed(value, NAME))

        view.enter_pressed_signal.connect(self.on_enter_pressed)

        view.btn_login.clicked.connect(self.login)
        view.btn_rg.clicked.connect(self.regist)

    def on_text_changed(self, value, index):
        model: LoginModel = self.model
        if index == USERNAME_L:
            model.username_login = value
        elif index == PASSWORD_L:
            model.password_login = value
        elif index == USERNAME_R:
            model.username_rg = value
        elif index == PASSWORD_R:
            model.password_rg = value
        elif index == CONFIRM_PASSWORD:
            model.confirm_password = value
        else:
            model.name = value

    def login(self):
        model: LoginModel = self.model

        username = model.username_login
        password = model.password_login
        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

        login_info = {"username": username, "password": hashed_password}

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                view: LoginView = self.view

                model.username_login = ""
                model.password_login = ""
                view.et_username_login.setText("")
                view.et_password_login.setText("")

                headers = reply.rawHeaderPairs()
                tokens = ""
                for header, value in headers:
                    if header == b"Authorization":
                        auth = value.data().decode("utf-8")
                        tokens = auth.split(" ")[1].split("/")

                self.setting_manager.set_refresh_token(tokens[0])
                self.setting_manager.set_access_token(tokens[1])
                self.set_home_signal.emit()

            else:
                self.api_manager.on_failure(reply)

        self.api_manager.login(api_handler, login_info)

    def regist(self):
        model: LoginModel = self.model

        name = model.name
        username = model.username_rg
        password = model.password_rg
        confirm_password = model.confirm_password

        if password != confirm_password:
            Toast().toast("비밀번호가 일치하지 않습니다.")
            return

        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

        registration_info = {"name": name, "username": username, "password": hashed_password}

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                view: LoginView = self.view

                Toast().toast("실험자 등록이 완료되었습니다.")
                model.name = ""
                model.username_rg = ""
                model.password_rg = ""
                model.confirm_password = ""
                view.et_name.setText("")
                view.et_username_rg.setText("")
                view.et_password_rg.setText("")
                view.et_confirm_password.setText("")

                view.set_tab_login()
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.regist(api_handler, registration_info)

    def on_enter_pressed(self, index):
        if index == 0:
            self.login()
        else:
            self.regist()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = LoginWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
