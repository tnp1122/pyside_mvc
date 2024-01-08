from PySide6.QtCore import QSettings


class Settings:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Settings, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.settings = QSettings("Jen Life", "PIT")

    def _save_str(self, key, value):
        self.settings.setValue(key, value)

    def _load_str(self, key):
        return self.settings.value(key)

    def _remove_str(self, key):
        self.settings.remove(key)

    def save_access_token(self, value):
        self._save_str("access_token", value)

    def save_refresh_token(self, value):
        self._save_str("refresh_token", value)

    def load_access_token(self):
        return self._load_str("access_token")

    def load_refresh_token(self):
        return self._load_str("refresh_token")


def main():
    settings = Settings()

    print(settings.load_access_token())


if __name__ == "__main__":
    main()
