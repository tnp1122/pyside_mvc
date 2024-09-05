from PySide6.QtCore import QObject, Signal

from models.snapshot import Timeline
from util.camera_manager import CameraUnit
from util.setting_manager import SettingManager


class PlateTimelineModel(QObject):
    selected_associations_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_associations = []

        self.timeline = []
        self.is_running = False

        self.camera_settings = {}

    def init_timeline_instance(self, timeline_name: str, target_name: str):
        self.timeline = Timeline(timeline_name, target_name, self.camera_settings)

    def get_camera_setting(self):
        camera_unit = CameraUnit()
        setting_manager = SettingManager()

        res_index = setting_manager.get_camera_resolution_index()
        res = camera_unit.cur.model.res[res_index]
        self.camera_settings["resolution"] = f"{res.width}*{res.height}"
        self.camera_settings["auto_expo"] = setting_manager.get_camera_auto_expo()
        self.camera_settings["expo_target"] = setting_manager.get_camera_expo_target()
        self.camera_settings["expo_time"] = setting_manager.get_camera_expo_time()
        self.camera_settings["expo_gain"] = setting_manager.get_camera_expo_gain()
        self.camera_settings["wb_temp"], self.camera_settings["wb_tint"] = setting_manager.get_camera_wb_temp_tint()
        r, g, b = setting_manager.get_camera_bb_rgb()
        self.camera_settings["bb_r"], self.camera_settings["bb_g"], self.camera_settings["bb_b"] = r, g, b
        self.camera_settings["saturation"] = setting_manager.get_camera_saturation()
        self.camera_settings["brightness"] = setting_manager.get_camera_brightness()
        self.camera_settings["contrast"] = setting_manager.get_camera_contrast()
        self.camera_settings["gamma"] = setting_manager.get_camera_gamma()
        self.camera_settings["anti_flicker_index"] = setting_manager.get_camera_anti_flicker()
