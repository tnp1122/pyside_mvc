from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QHBoxLayout

from ui.common import BaseWidgetView
from util.setting_manager import SettingManager


class SettingView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        lyt = QVBoxLayout(self)

        self.btn = QPushButton("홈")
        self.btn_logout = QPushButton("로그아웃")

        setting_manager = SettingManager()
        lb_version = QLabel("버전: ")
        lb_version_str = QLabel(setting_manager.get_pit_version())
        lyt_version = QHBoxLayout()
        lyt_version.addWidget(lb_version)
        lyt_version.addWidget(lb_version_str)

        lyt.addStretch()
        lyt.addWidget(self.btn)
        lyt.addWidget(self.btn_logout)
        lyt.addLayout(lyt_version)
        lyt.addStretch()
