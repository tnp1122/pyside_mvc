import json

from PySide6.QtCore import QSettings

VERSION = "version"
USE_NETWORK_DB = "use_network_db"

ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"
EXPERIMENTER_NAME = "experimenter_name"

USE_METAL_SAMPLE = "use_metal_sample"
USE_ADDITIVE_SAMPLE = "use_additive_sample"
USE_TARGET_MATERIAL = "use_target_material"

PATH_TO_LOAD_IMAGE = "path_to_load_image"
MASK_AREA_INFO = "mask_area_info"


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

    def _set_json_value(self, key, data):
        json_str = json.dumps(data)
        self._set_value(key, json_str)

    def _get_value(self, key, default_value=None):
        return self.settings.value(key, default_value)

    def _get_json_data(self, key):
        json_str: str = self._get_value(key)
        if json_str:
            return json.loads(json_str)
        else:
            return dict()

    def _remove_value(self, key):
        self.settings.remove(key)

    def get_pit_version(self):
        return self._get_value(VERSION, "unknown")

    def set_use_network_db(self, value):
        self._set_value(USE_NETWORK_DB, value)

    def get_use_network_db(self):
        return self._get_value(USE_NETWORK_DB)

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

    def set_experimenter_name(self, name):
        self._set_value(EXPERIMENTER_NAME, name)

    def get_experimenter_name(self):
        return self._get_value(EXPERIMENTER_NAME)

    def remove_experimenter_name(self):
        self._remove_value(EXPERIMENTER_NAME)

    def set_use_metal_samples(self, samples):
        if isinstance(samples, set):
            samples = list(samples)
        self._set_value(USE_METAL_SAMPLE, samples)

    def get_use_metal_samples(self):
        use_metal_samples = self._get_value(USE_METAL_SAMPLE, [])
        use_metal_samples = set([int(sample_id) for sample_id in use_metal_samples])

        return use_metal_samples

    def set_use_additive_samples(self, samples):
        if isinstance(samples, set):
            samples = list(samples)
        self._set_value(USE_ADDITIVE_SAMPLE, samples)

    def get_use_additive_samples(self):
        use_additive_samples = self._get_value(USE_ADDITIVE_SAMPLE, [])
        use_additive_samples = set([int(sample_id) for sample_id in use_additive_samples])

        return use_additive_samples

    def set_path_to_load_image(self, image_path):
        self._set_value(PATH_TO_LOAD_IMAGE, image_path)

    def get_path_to_load_image(self):
        return self._get_value(PATH_TO_LOAD_IMAGE)

    def set_mask_area_info(self, area_info):
        self._set_json_value(MASK_AREA_INFO, area_info)

    def get_mask_area_info(self):
        # 초기값 임시 고정
        mask_area_info = self._get_json_data(MASK_AREA_INFO)
        mask_area_info["x"] = 2002
        mask_area_info["y"] = 704
        mask_area_info["width"] = 2145
        mask_area_info["height"] = 1439
        mask_area_info["radius"] = 30
        mask_area_info["flare_threshold"] = 185
        return mask_area_info


def main():
    settings = SettingManager()

    print(settings.get_access_token())


if __name__ == "__main__":
    main()
