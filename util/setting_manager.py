from PySide6.QtCore import QSettings

ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"
USE_NETWORK_DB = "use_network_db"
NOT_USE_METAL_SAMPLE = "not_use_metal_sample"
NOT_USE_ADDITIVE_SAMPLE = "not_use_additive_sample"


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

    def _get_value(self, key, default_value=None):
        return self.settings.value(key, default_value)

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

    def set_not_use_metal_samples(self, samples):
        if isinstance(samples, set):
            samples = list(samples)
        self._set_value(NOT_USE_METAL_SAMPLE, samples)

    def get_not_use_metal_samples(self):
        not_use = self._get_value(NOT_USE_METAL_SAMPLE, [])
        not_use = set([int(sample_id) for sample_id in not_use])

        return not_use

    def set_not_use_additive_samples(self, samples):
        if isinstance(samples, set):
            samples = list(samples)
        self._set_value(NOT_USE_ADDITIVE_SAMPLE, samples)

    def get_not_use_additive_samples(self):
        not_use = self._get_value(NOT_USE_ADDITIVE_SAMPLE, [])
        not_use = set([int(sample_id) for sample_id in not_use])

        return not_use


def main():
    settings = SettingManager()

    print(settings.get_access_token())


if __name__ == "__main__":
    main()
