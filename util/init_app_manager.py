from data.api.api_manager import APIManager
from util.setting_manager import SettingManager

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

    def logout(self):
        self.setting_manager.remove_access_token()
        self.setting_manager.remove_refresh_token()
        self.setting_manager.remove_experimenter_name()
        self.user_info = {}
