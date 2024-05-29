from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QWidget

from ui.common import BaseStackedWidgetView
from ui.tabs.first_tab.setting.camera import SettingCameraController
from util.setting_manager import SettingManager


class SettingView(BaseStackedWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        self.btn_home = QPushButton("홈")
        self.btn_set_camera = QPushButton("카메라 설정")
        self.btn_logout = QPushButton("로그아웃")

        setting_manager = SettingManager()
        lb_version = QLabel("버전: ")
        lb_version_str = QLabel(setting_manager.get_pit_version())
        lyt_version = QHBoxLayout()
        lyt_version.addWidget(lb_version)
        lyt_version.addWidget(lb_version_str)

        setting_view = QWidget()
        lyt = QVBoxLayout(setting_view)
        lyt.addStretch()
        lyt.addWidget(self.btn_home)
        lyt.addWidget(self.btn_set_camera)
        lyt.addWidget(self.btn_logout)
        lyt.addLayout(lyt_version)
        lyt.addStretch()

        self.addWidget(self.with_container(setting_view))

    def show_set_camera_widget(self):
        self.widget_set_camera = SettingCameraController()
        self.addWidget(self.widget_set_camera.view)

    def on_close_set_camera_widget(self):
        self.removeWidget(self.widget_set_camera.view)
        self.widget_set_camera.close()
        self.widget_set_camera = None
