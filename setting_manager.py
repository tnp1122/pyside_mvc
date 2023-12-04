from PySide6.QtCore import QSettings


class SettingManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(SettingManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.settings = QSettings("Jen Life", "PIT")

    def save_str(self, key, value):
        self.settings.setValue(key, value)

    def load_str(self, key):
        return self.settings.value(key)

    def save_access_token(self, value):
        self.save_str("access_token", value)

    def save_refresh_token(self, value):
        self.save_str("refresh_token", value)

    def load_access_token(self):
        return self.load_str("access_token")

    def load_refresh_token(self):
        return self.load_str("refresh_token")
