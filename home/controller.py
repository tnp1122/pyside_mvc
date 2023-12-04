import json

from PySide6.QtNetwork import QNetworkReply, QNetworkRequest

from setting_manager import SettingManager
from data.api.api_manager import APIManager


class HomeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.api_manager = APIManager()
        # self.api_manager.manager.finished.connect(self.set_api_handler)
        # self.set_api_handler()

    def set_username_login(self, value):
        self.model.username_login = value

    def set_password_login(self, value):
        self.model._password_login = value

    def set_username_rg(self, value):
        self.model.username_rg = value

    def set_password_rg(self, value):
        self.model.password_rg = value

    def set_name(self, value):
        self.model.name = value

    def do_login(self):
        username = self.model.username_login
        password = self.model.password_login

        login_info = {"username": username, "password": password}

        def api_handler(reply):
            data = reply.readAll().data().decode("utf-8")
            print("reply:", reply)
            print("data:", data)
            http_status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            endpoint = reply.property("api_endpoint")
            print(f"HTTP Status Code: {http_status_code}")
            print(f"API Endpoint: {endpoint}")

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
                setting_manager = SettingManager()
                setting_manager.save_refresh_token(tokens[0])
                setting_manager.save_access_token(tokens[1])

        self.api_manager.login(login_info, api_handler)

    def do_registration(self):
        name = self.model.name
        username = self.model.username_rg
        password = self.model.password_rg

        registration_info = {"name": name, "username": username, "password": password}

        def api_handler(reply):
            data = reply.readAll().data().decode("utf-8")
            print("reply:", reply)
            print("data:", data)
            http_status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            endpoint = reply.property("api_endpoint")
            print(f"HTTP Status Code: {http_status_code}")
            print(f"API Endpoint: {endpoint}")

            if reply.error() == QNetworkReply.NoError:
                data = reply.readAll().data().decode("utf-8")
                print(f"응답 성공\ndata:", data)
                headers = reply.rawHeaderPairs()
                for header in headers:
                    print(f"Header: {header[0]} = {header[1].data().decode('utf-8')}")

            else:
                print(f"에러 발생: {reply.errorString()}")

        self.api_manager.regist(registration_info, api_handler)
        # self.api_manager.dummy(api_handler)
