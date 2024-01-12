import json

from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from util import SettingManager
from util.enums import FirstTabIndex


class InitAppManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InitAppManager, cls).__new__(cls)

            return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.setting_manager = SettingManager()
            self.api_manager = APIManager()
            self.user_info = {}

    def _use_network_db(self):
        return True
        if self.setting_manager.get_use_network_db():
            return True
        else:
            return False

    def get_user_info(self, handler):
        def _get_user_api_handler(reply):
            data = reply.readAll().data().decode("utf-8")

            if reply.error() == QNetworkReply.NoError:
                user_info = json.loads(data)
                self.user_info = {"username": user_info["username"], "name": user_info["name"]}
                handler(FirstTabIndex.HOME)
            else:
                print(reply)
                print(reply.error)
                print(reply.readAll().data().decode("utf-8"))
                handler(FirstTabIndex.LOGIN)

        self.api_manager.get_user_info(callback=_get_user_api_handler)

    def get_first_tab_index(self, handler):
        if self._use_network_db():
            if self.setting_manager.get_access_token():
                self.get_user_info(handler=handler)
            else:
                handler(FirstTabIndex.LOGIN)
            return
        handler(FirstTabIndex.HOME)

    def logout(self):
        self.setting_manager.remove_access_token()
        self.setting_manager.remove_refresh_token()
        self.user_info = {}
