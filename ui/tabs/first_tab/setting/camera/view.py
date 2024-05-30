import logging

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout

from ui.common import BaseWidgetView, ImageButton, SetCamera

from util.camera_manager import CameraUnit, toupcam
from util import local_storage_manager as lsm
from util import image_converter as ic


class SettingCameraView(BaseWidgetView):
    camera_unit = CameraUnit()

    def __init__(self, parent=None):
        super().__init__(parent)

        img_back_arrow = lsm.get_static_image_path("expand_arrow.png")
        self.btn_back = ImageButton(img_back_arrow, angle=90)
        lb_header = QLabel("카메라 설정")

        lyt_header = QHBoxLayout()
        lyt_header.addWidget(self.btn_back)
        lyt_header.addStretch()
        lyt_header.addWidget(lb_header)
        lyt_header.addStretch()

        # 설정
        """ 설정 스크롤 위젯"""
        # scl_setting = QScrollArea()
        set_camera = SetCamera()

        # 카메라 라벨
        self.lb_video = QLabel()
        self.lb_video.setMinimumSize(540, 810)

        lyt_content = QHBoxLayout()
        lyt_content.addWidget(set_camera)
        lyt_content.addStretch()
        lyt_content.addWidget(self.lb_video)
        lyt_content.addStretch()

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_header)
        lyt.addLayout(lyt_content)
        lyt.addStretch()

        self.camera_unit.evtCallback.connect(self.on_event_callback)
        self.camera_unit.signal_image.connect(self.update_video)

    def update_video(self, image: np.ndarray):
        if image is not None:
            pixmap = ic.array_to_q_pixmap(image, True)
            self.lb_video.setPixmap(pixmap.scaled(self.lb_video.size(), Qt.KeepAspectRatio))

    """ 이벤트 핸들러 """

    def on_event_callback(self, nEvent):
        if self.camera_unit.cam:
            if nEvent == toupcam.TOUPCAM_EVENT_ERROR:
                self.camera_unit.close_camera()
                logging.error("Generic Error.: 카메라 상태를 확인하세요.")