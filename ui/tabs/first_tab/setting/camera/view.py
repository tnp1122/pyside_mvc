import logging

import numpy as np
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QGroupBox, QCheckBox, QSlider, QPushButton, \
    QScrollArea

from ui.common import BaseWidgetView, ImageButton

from util.camera_manager import CameraUnit, toupcam
from util import local_storage_manager as lsm
from util import image_converter as ic


class SettingCameraView(BaseWidgetView):
    camera_unit = CameraUnit()

    @staticmethod
    def get_slider_layout(lb1, lb2, slider):
        hlyt = QHBoxLayout()
        hlyt.addWidget(lb1)
        hlyt.addStretch()
        hlyt.addWidget(lb2)
        lyt = QVBoxLayout()
        lyt.addLayout(hlyt)
        lyt.addWidget(slider)

        return lyt

    def __init__(self, parent=None):
        super().__init__(parent)

        camera_unit: CameraUnit = self.camera_unit
        self.camera_started = camera_unit.pData is not None

        img_back_arrow = lsm.get_static_image_path("expand_arrow.png")
        self.btn_back = ImageButton(img_back_arrow, angle=90)
        lb_header = QLabel("카메라 설정")

        lyt_header = QHBoxLayout()
        lyt_header.addWidget(self.btn_back)
        lyt_header.addStretch()
        lyt_header.addWidget(lb_header)
        lyt_header.addStretch()

        # 설정
        """ 해상도 """
        self.cmb_res = QComboBox()
        self.cmb_res.setEnabled(False)
        lyt_res = QVBoxLayout()
        lyt_res.addWidget(self.cmb_res)
        gbox_res = QGroupBox("해상도")
        gbox_res.setLayout(lyt_res)
        self.cmb_res.currentIndexChanged.connect(lambda index: self.camera_unit.set_resolution(index))

        """ 노출 """
        self.cb_auto_expo = QCheckBox("자동 노출")
        self.lb_expo_time = QLabel("0")
        self.lb_expo_gain = QLabel("0")
        self.slider_expo_time = QSlider(Qt.Horizontal)
        self.slider_expo_gain = QSlider(Qt.Horizontal)
        self.slider_expo_time.setEnabled(self.camera_started)
        self.slider_expo_gain.setEnabled(self.camera_started)
        lyt_expo = QVBoxLayout()
        lyt_expo.addWidget(self.cb_auto_expo)
        lyt_expo.addLayout(self.get_slider_layout(QLabel("시간(us):"), self.lb_expo_time, self.slider_expo_time))
        lyt_expo.addLayout(self.get_slider_layout(QLabel("게인(%):"), self.lb_expo_gain, self.slider_expo_gain))
        gbox_expo = QGroupBox("노출")
        gbox_expo.setLayout(lyt_expo)
        self.cb_auto_expo.stateChanged.connect(self.on_auto_expo_changed)
        self.slider_expo_time.valueChanged.connect(self.on_expo_time_changed)
        self.slider_expo_gain.valueChanged.connect(self.on_expo_gain_changed)

        # """ 화이트 밸런스 """
        self.lb_temp = QLabel(str(toupcam.TOUPCAM_TEMP_DEF))
        self.lb_tint = QLabel(str(toupcam.TOUPCAM_TINT_DEF))
        self.slider_temp = QSlider(Qt.Horizontal)
        self.slider_tint = QSlider(Qt.Horizontal)
        self.slider_temp.setRange(toupcam.TOUPCAM_TEMP_MIN, toupcam.TOUPCAM_TEMP_MAX)
        self.slider_temp.setValue(toupcam.TOUPCAM_TEMP_DEF)
        self.slider_tint.setRange(toupcam.TOUPCAM_TINT_MIN, toupcam.TOUPCAM_TINT_MAX)
        self.slider_tint.setValue(toupcam.TOUPCAM_TINT_DEF)
        self.slider_temp.setEnabled(self.camera_started)
        self.slider_tint.setEnabled(self.camera_started)
        self.slider_temp.valueChanged.connect(self.on_WB_temp_changed)
        self.slider_tint.valueChanged.connect(self.on_WB_tint_changed)
        self.btn_auto_WB = QPushButton("화이트 밸런스")
        self.btn_auto_WB.setEnabled(self.camera_started)
        self.btn_auto_WB.clicked.connect(self.camera_unit.set_auto_WB)
        lyt_WB = QVBoxLayout()
        lyt_WB.addLayout(self.get_slider_layout(QLabel("색온도:"), self.lb_temp, self.slider_temp))
        lyt_WB.addLayout(self.get_slider_layout(QLabel("색조:"), self.lb_tint, self.slider_tint))
        lyt_WB.addWidget(self.btn_auto_WB)
        gbox_WB = QGroupBox("화이트 밸런스")
        gbox_WB.setLayout(lyt_WB)

        """ 설정 스크롤 위젯"""
        scl_setting = QScrollArea()
        lyt_setting = QVBoxLayout(scl_setting)
        lyt_setting.addWidget(gbox_res)
        lyt_setting.addWidget(gbox_expo)
        lyt_setting.addWidget(gbox_WB)
        lyt_setting.addStretch()

        # 카메라 라벨
        self.lb_video = QLabel()
        self.lb_video.setMinimumSize(540, 810)

        lyt_content = QHBoxLayout()
        lyt_content.addWidget(scl_setting)
        lyt_content.addStretch()
        lyt_content.addWidget(self.lb_video)
        lyt_content.addStretch()

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_header)
        lyt.addLayout(lyt_content)
        lyt.addStretch()

        camera_unit.evtCallback.connect(self.on_event_callback)
        camera_unit.signal_image.connect(self.update_video)

    def init_view(self):
        super().init_view()

        if self.camera_started:
            self.set_cmb_resolution()

            camera_unit: CameraUnit = self.camera_unit
            uimin, uimax, uidef = camera_unit.cam.get_ExpTimeRange()
            usmin, usmax, usdef = camera_unit.cam.get_ExpoAGainRange()
            self.slider_expo_time.setRange(uimin, 350000)
            self.slider_expo_time.setValue(uidef)
            self.slider_expo_gain.setRange(usmin, 500)
            self.slider_expo_gain.setValue(usdef)

            self.handle_expo_event()
            if camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0:
                self.handle_temp_tint_event()

            self.btn_auto_WB.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            self.slider_temp.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            self.slider_tint.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            b_auto = camera_unit.cam.get_AutoExpoEnable()
            self.cb_auto_expo.setChecked(b_auto == 1)

    def update_video(self, image: np.ndarray):
        if image is not None:
            pixmap = ic.array_to_q_pixmap(image, True)
            self.lb_video.setPixmap(pixmap.scaled(self.lb_video.size(), Qt.KeepAspectRatio))

    def set_cmb_resolution(self):
        self.cmb_res.clear()
        camera_unit: CameraUnit = self.camera_unit
        if self.camera_started:
            for i in range(camera_unit.cur.model.preview):
                res = camera_unit.cur.model.res[i]
                self.cmb_res.addItem(f"{res.width}*{res.height}")
            self.cmb_res.setCurrentIndex(camera_unit.res)
        self.cmb_res.setEnabled(True)

    def on_auto_expo_changed(self, state):
        if self.camera_unit.set_auto_expo(state):
            self.slider_expo_time.setEnabled(not state)
            self.slider_expo_gain.setEnabled(not state)

    def on_expo_time_changed(self, value):
        if self.camera_unit.set_expo_time(value):
            self.lb_expo_time.setText(str(value))

    def on_expo_gain_changed(self, value):
        if self.camera_unit.set_expo_gain(value):
            self.lb_expo_gain.setText(str(value))

    def on_WB_temp_changed(self, value):
        if self.camera_unit.set_WB_temp(value):
            self.lb_temp.setText(str(value))

    def on_WB_tint_changed(self, value):
        if self.camera_unit.set_WB_tint(value):
            self.lb_tint.setText(set(value))

    def handle_expo_event(self):
        unit: CameraUnit = self.camera_unit
        time = unit.cam.get_ExpoTime()
        gain = unit.cam.get_ExpoAGain()
        with QSignalBlocker(self.slider_expo_time):
            self.slider_expo_time.setValue(time)
        with QSignalBlocker(self.slider_expo_gain):
            self.slider_expo_gain.setValue(gain)
        self.lb_expo_time.setText(str(time))
        self.lb_expo_gain.setText(str(gain))

    def handle_temp_tint_event(self):
        unit: CameraUnit = self.camera_unit
        nTemp, nTint = unit.cam.get_TempTint()
        with QSignalBlocker(self.slider_temp):
            self.slider_temp.setValue(nTemp)
        with QSignalBlocker(self.slider_tint):
            self.slider_tint.setValue(nTint)
        self.lb_temp.setText(str(nTemp))
        self.lb_tint.setText(str(nTint))

    def on_event_callback(self, nEvent):
        if self.camera_unit.cam:
            if nEvent == toupcam.TOUPCAM_EVENT_EXPOSURE:
                self.handle_expo_event()
            elif nEvent == toupcam.TOUPCAM_EVENT_TEMPTINT:
                self.handle_temp_tint_event()
            elif nEvent == toupcam.TOUPCAM_EVENT_ERROR:
                self.camera_unit.close_camera()
                logging.error("Generic Error.: 카메라 상태를 확인하세요.")
