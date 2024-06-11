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

CAMERA_RESOLUTION = "camera_resolution"
CAMERA_AUTO_EXPO = "camera_auto_expo"
CAMERA_EXPO_TARGET = "camera_expo_target"
CAMERA_EXPO_TIME = "camera_expo_time"
CAMERA_EXPO_GAIN = "camera_expo_gain"
CAMERA_WB_TEMP = "camera_wb_temp"
CAMERA_WB_TINT = "camera_wb_tint"
CAMERA_BB_R = "camera_bb_r"
CAMERA_BB_G = "camera_bb_g"
CAMERA_BB_B = "camera_bb_b"
CAMERA_HUE = "camera_hue"
CAMERA_SATURATION = "camera_saturation"
CAMERA_BRIGHTNESS = "camera_brightness"
CAMERA_CONTRAST = "camera_contrast"
CAMERA_GAMMA = "camera_gamma"
CAMERA_ANTI_FLICKER = "camera_anti_flicker"


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
        self.set_mask_area_info(mask_area_info)
        return mask_area_info

    # 카메라 관련

    def set_camera_resolution_index(self, index):
        self._set_value(CAMERA_RESOLUTION, index)

    def get_camera_resolution_index(self):
        return self._get_value(CAMERA_RESOLUTION)

    def set_camera_auto_expo(self, value):
        self._set_value(CAMERA_AUTO_EXPO, value)

    def get_camera_auto_expo(self):
        return self._get_value(CAMERA_AUTO_EXPO)

    def set_camera_expo_target(self, value):
        self._set_value(CAMERA_EXPO_TARGET, value)

    def get_camera_expo_target(self):
        return self._get_value(CAMERA_EXPO_TARGET)

    def set_camera_expo_time(self, slider_value):
        self._set_value(CAMERA_EXPO_TIME, slider_value)

    def get_camera_expo_time(self):
        return self._get_value(CAMERA_EXPO_TIME)

    def set_camera_expo_gain(self, value):
        self._set_value(CAMERA_EXPO_GAIN, value)

    def get_camera_expo_gain(self):
        return self._get_value(CAMERA_EXPO_GAIN)

    def set_camera_wb_temp_tint(self, temp=None, tint=None):
        if temp is not None:
            self._set_value(CAMERA_WB_TEMP, temp)
        if tint is not None:
            self._set_value(CAMERA_WB_TINT, tint)

    def get_camera_wb_temp_tint(self):
        temp = self._get_value(CAMERA_WB_TEMP)
        tint = self._get_value(CAMERA_WB_TINT)
        return temp, tint

    def set_camera_bb_rgb(self, r=None, g=None, b=None):
        if r is not None:
            self._set_value(CAMERA_BB_R, r)
        if g is not None:
            self._set_value(CAMERA_BB_G, g)
        if b is not None:
            self._set_value(CAMERA_BB_B, b)

    def get_camera_bb_rgb(self):
        r = self._get_value(CAMERA_BB_R)
        g = self._get_value(CAMERA_BB_G)
        b = self._get_value(CAMERA_BB_B)
        return r, g, b

    def set_camera_hue(self, value):
        self._set_value(CAMERA_HUE, value)

    def get_camera_hue(self):
        return self._get_value(CAMERA_HUE)

    def set_camera_saturation(self, value):
        self._set_value(CAMERA_SATURATION, value)

    def get_camera_saturation(self):
        return self._get_value(CAMERA_SATURATION)

    def set_camera_brightness(self, value):
        self._set_value(CAMERA_BRIGHTNESS, value)

    def get_camera_brightness(self):
        return self._get_value(CAMERA_BRIGHTNESS)

    def set_camera_contrast(self, value):
        self._set_value(CAMERA_CONTRAST, value)

    def get_camera_contrast(self):
        return self._get_value(CAMERA_CONTRAST)

    def set_camera_gamma(self, value):
        self._set_value(CAMERA_GAMMA, value)

    def get_camera_gamma(self):
        return self._get_value(CAMERA_GAMMA)

    def set_camera_anti_flicker(self, index):
        self._set_value(CAMERA_ANTI_FLICKER, index)

    def get_camera_anti_flicker(self):
        return self._get_value(CAMERA_ANTI_FLICKER, 2)


def main():
    settings = SettingManager()

    print(settings.get_access_token())


if __name__ == "__main__":
    main()
