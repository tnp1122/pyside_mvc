from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout

from ui.common import BaseWidgetView, ImageButton
from ui.common.camera_widget import CameraWidget
from util import local_storage_manager as lsm


class SettingCameraView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

        img_back_arrow = lsm.get_static_image_path("expand_arrow.png")
        self.btn_back = ImageButton(img_back_arrow, angle=90)
        lb_header = QLabel("카메라 설정")

        lyt_header = QHBoxLayout()
        lyt_header.addWidget(self.btn_back)
        lyt_header.addWidget(lb_header)
        lyt_header.addStretch()

        camera_widget = CameraWidget()
        lyt_content = QHBoxLayout()
        lyt_content.addWidget(camera_widget)
        lyt_content.addStretch()

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_header)
        lyt.addLayout(lyt_content)
