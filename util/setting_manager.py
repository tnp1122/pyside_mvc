from PySide6.QtCore import QSettings

ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"
USE_NETWORK_DB = "use_network_db"


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

    def _set_value(self, key, value):
        self.settings.setValue(key, value)

    def _get_value(self, key):
        return self.settings.value(key)

    def _remove_value(self, key):
        self.settings.remove(key)

    def set_access_token(self, value):
        self._set_value(ACCESS_TOKEN, value)

    def get_access_token(self):
        return self._get_value(ACCESS_TOKEN)

    def remove_access_token(self):
        self._remove_value(ACCESS_TOKEN)

    def set_refresh_token(self, value):
        self._set_value(REFRESH_TOKEN, value)

    def get_refresh_token(self):
        return self._get_value(REFRESH_TOKEN)

    def remove_refresh_token(self):
        self._remove_value(REFRESH_TOKEN)

    def set_use_network_db(self, value):
        self._set_value(USE_NETWORK_DB, value)

    def get_use_network_db(self):
        return self._get_value(USE_NETWORK_DB)


def main():
    settings = SettingManager()

    print(settings.get_access_token())


if __name__ == "__main__":
    main()
