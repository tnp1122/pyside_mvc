import numpy as np
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtWidgets import QScrollArea, QHBoxLayout, QVBoxLayout, QComboBox, QGroupBox, QCheckBox, QLabel, QSlider, \
    QPushButton, QWidget, QSizePolicy

from util.camera_manager import CameraUnit, toupcam


class ExponentialFunction:
    def __init__(self, x1, y1, x2, y2):
        self.b = (np.log(y2) - np.log(y1)) / (x2 - x1)
        self.a = y1 / np.exp(self.b * x1)

    def calculate_x(self, y):
        return (np.log(y / self.a)) / self.b

    def calculate_y(self, x):
        return self.a * np.exp(self.b * x)


def get_slider_layout(lb1, lb2, slider):
    hlyt = QHBoxLayout()
    hlyt.addWidget(lb1)
    hlyt.addStretch()
    hlyt.addWidget(lb2)
    lyt = QVBoxLayout()
    lyt.addLayout(hlyt)
    lyt.addWidget(slider)

    return lyt


def get_twin_button_layout(btn1, btn2):
    lyt = QHBoxLayout()
    lyt.addWidget(btn1)
    lyt.addWidget(btn2)

    return lyt


class SetCamera(QScrollArea):
    camera_unit = CameraUnit()

    def __init__(self, parent=None):
        super().__init__(parent)

        camera_unit: CameraUnit = self.camera_unit
        time_min, time_max, _ = camera_unit.cam.get_ExpTimeRange()
        self.exponential_function = ExponentialFunction(0, time_min, 100, time_max)
        self.camera_started = camera_unit.pData is not None

        """ 해상도 """
        self.cmb_res = QComboBox()
        self.cmb_res.setEnabled(False)
        lyt_res = QVBoxLayout()
        lyt_res.addWidget(self.cmb_res)
        gbox_res = QGroupBox("해상도")
        gbox_res.setLayout(lyt_res)
        self.cmb_res.currentIndexChanged.connect(lambda index: self.camera_unit.set_resolution(index))

        """ 노출 및 게인"""
        self.cb_auto_expo = QCheckBox("자동 노출")
        self.lb_expo_target = QLabel("0")
        self.lb_expo_time = QLabel("0")
        self.lb_expo_gain = QLabel("0")
        self.slider_expo_target = QSlider(Qt.Horizontal)
        self.slider_expo_time = QSlider(Qt.Horizontal)
        self.slider_expo_gain = QSlider(Qt.Horizontal)
        self.slider_expo_target.setEnabled(self.camera_started)
        self.slider_expo_time.setEnabled(self.camera_started)
        self.slider_expo_gain.setEnabled(self.camera_started)
        lyt_expo = QVBoxLayout()
        lyt_expo.addWidget(self.cb_auto_expo)
        lyt_expo.addLayout(get_slider_layout(QLabel("타겟: "), self.lb_expo_target, self.slider_expo_target))
        lyt_expo.addLayout(get_slider_layout(QLabel("노출 시간:"), self.lb_expo_time, self.slider_expo_time))
        lyt_expo.addLayout(get_slider_layout(QLabel("게인:"), self.lb_expo_gain, self.slider_expo_gain))
        gbox_expo = QGroupBox("노출 및 게인")
        gbox_expo.setLayout(lyt_expo)
        self.cb_auto_expo.stateChanged.connect(self.on_auto_expo_changed)
        self.slider_expo_target.valueChanged.connect(self.on_expo_target_changed)
        self.slider_expo_time.valueChanged.connect(self.on_expo_time_changed)
        self.slider_expo_gain.valueChanged.connect(self.on_expo_gain_changed)

        """ 화이트 밸런스 """
        self.lb_temp = QLabel(str(toupcam.TOUPCAM_TEMP_DEF))
        self.lb_tint = QLabel(str(toupcam.TOUPCAM_TINT_DEF))
        self.slider_temp = QSlider(Qt.Horizontal)
        self.slider_tint = QSlider(Qt.Horizontal)
        self.slider_temp.setRange(toupcam.TOUPCAM_TEMP_MIN, toupcam.TOUPCAM_TEMP_MAX)
        self.slider_tint.setRange(toupcam.TOUPCAM_TINT_MIN, toupcam.TOUPCAM_TINT_MAX)
        self.slider_temp.setValue(toupcam.TOUPCAM_TEMP_DEF)
        self.slider_tint.setValue(toupcam.TOUPCAM_TINT_DEF)
        self.slider_temp.setEnabled(self.camera_started)
        self.slider_tint.setEnabled(self.camera_started)
        self.slider_temp.valueChanged.connect(self.on_WB_temp_changed)
        self.slider_tint.valueChanged.connect(self.on_WB_tint_changed)
        self.btn_auto_WB = QPushButton("화이트 밸런스")
        self.btn_auto_WB.setEnabled(self.camera_started)
        self.btn_auto_WB.clicked.connect(self.camera_unit.auto_white_balance_once)
        self.btn_init_WB = QPushButton("기본값")
        self.btn_init_WB.setEnabled(self.camera_started)
        self.btn_init_WB.clicked.connect(self.init_white_balance)
        lyt_WB = QVBoxLayout()
        lyt_WB.addLayout(get_slider_layout(QLabel("색 온도:"), self.lb_temp, self.slider_temp))
        lyt_WB.addLayout(get_slider_layout(QLabel("색조:"), self.lb_tint, self.slider_tint))
        lyt_WB.addLayout(get_twin_button_layout(self.btn_auto_WB, self.btn_init_WB))
        gbox_WB = QGroupBox("화이트 밸런스")
        gbox_WB.setLayout(lyt_WB)

        """ 블랙 밸런스 """
        rgb = camera_unit.rgb
        self.lb_r = QLabel(str(rgb[0]))
        self.lb_g = QLabel(str(rgb[1]))
        self.lb_b = QLabel(str(rgb[2]))
        self.slider_r = QSlider(Qt.Horizontal)
        self.slider_g = QSlider(Qt.Horizontal)
        self.slider_b = QSlider(Qt.Horizontal)
        self.slider_r.setRange(0, 240)
        self.slider_g.setRange(0, 240)
        self.slider_b.setRange(0, 240)
        self.slider_r.setValue(rgb[0])
        self.slider_g.setValue(rgb[1])
        self.slider_b.setValue(rgb[2])
        self.slider_r.setEnabled(self.camera_started)
        self.slider_g.setEnabled(self.camera_started)
        self.slider_b.setEnabled(self.camera_started)
        self.slider_r.valueChanged.connect(lambda value: self.on_black_balance_changed(0, value))
        self.slider_g.valueChanged.connect(lambda value: self.on_black_balance_changed(1, value))
        self.slider_b.valueChanged.connect(lambda value: self.on_black_balance_changed(2, value))
        self.btn_auto_BB = QPushButton("블랙 밸런스")
        self.btn_auto_BB.setEnabled(self.camera_started)
        self.btn_auto_BB.clicked.connect(self.camera_unit.auto_black_blance_once)
        self.btn_init_BB = QPushButton("기본값")
        self.btn_init_BB.setEnabled(self.camera_started)
        self.btn_init_BB.clicked.connect(self.init_black_balance)
        lyt_BB = QVBoxLayout()
        lyt_BB.addLayout(get_slider_layout(QLabel("빨강:"), self.lb_r, self.slider_r))
        lyt_BB.addLayout(get_slider_layout(QLabel("녹색:"), self.lb_g, self.slider_g))
        lyt_BB.addLayout(get_slider_layout(QLabel("파랑:"), self.lb_b, self.slider_b))
        lyt_BB.addLayout(get_twin_button_layout(self.btn_auto_BB, self.btn_init_BB))
        gbox_BB = QGroupBox("블랙 밸런스")
        gbox_BB.setLayout(lyt_BB)

        """ 색 조정 """
        h_def, h_min, h_max = toupcam.TOUPCAM_HUE_DEF, toupcam.TOUPCAM_HUE_MIN, toupcam.TOUPCAM_HUE_MAX
        s_def, s_min, s_max = toupcam.TOUPCAM_SATURATION_DEF, toupcam.TOUPCAM_SATURATION_MIN, toupcam.TOUPCAM_SATURATION_MAX
        b_def, b_min, b_max = toupcam.TOUPCAM_BRIGHTNESS_DEF, toupcam.TOUPCAM_BRIGHTNESS_MIN, toupcam.TOUPCAM_BRIGHTNESS_MAX
        c_def, c_min, c_max = toupcam.TOUPCAM_CONTRAST_DEF, toupcam.TOUPCAM_CONTRAST_MIN, toupcam.TOUPCAM_CONTRAST_MAX
        g_def, g_min, g_max = toupcam.TOUPCAM_GAMMA_DEF, toupcam.TOUPCAM_GAMMA_MIN, toupcam.TOUPCAM_GAMMA_MAX
        self.lb_hue = QLabel(str(h_def))
        self.lb_saturation = QLabel(str(s_def))
        self.lb_brightness = QLabel(str(b_def))
        self.lb_contrast = QLabel(str(c_def))
        self.lb_gamma = QLabel(str(g_def))
        self.slider_hue = QSlider(Qt.Horizontal)
        self.slider_hue.setRange(h_min, h_max)
        self.slider_hue.setValue(h_def)
        self.slider_hue.setEnabled(self.camera_started)
        self.slider_hue.valueChanged.connect(self.on_hue_changed)
        self.slider_saturation = QSlider(Qt.Horizontal)
        self.slider_saturation.setRange(s_min, s_max)
        self.slider_saturation.setValue(s_def)
        self.slider_saturation.setEnabled(self.camera_started)
        self.slider_saturation.valueChanged.connect(self.on_saturation_changed)
        self.slider_brightness = QSlider(Qt.Horizontal)
        self.slider_brightness.setRange(b_min, b_max)
        self.slider_brightness.setValue(b_def)
        self.slider_brightness.setEnabled(self.camera_started)
        self.slider_brightness.valueChanged.connect(self.on_brightness_changed)
        self.slider_contrast = QSlider(Qt.Horizontal)
        self.slider_contrast.setRange(c_min, c_max)
        self.slider_contrast.setValue(c_def)
        self.slider_contrast.setEnabled(self.camera_started)
        self.slider_contrast.valueChanged.connect(self.on_contrast_changed)
        self.slider_gamma = QSlider(Qt.Horizontal)
        self.slider_gamma.setRange(g_min, g_max)
        self.slider_gamma.setValue(g_def)
        self.slider_gamma.setEnabled(self.camera_started)
        self.slider_gamma.valueChanged.connect(self.on_gamma_changed)
        self.btn_init_color = QPushButton("기본값")
        self.btn_init_color.setEnabled(self.camera_started)
        self.btn_init_color.clicked.connect(self.init_color)
        lyt_color = QVBoxLayout()
        lyt_color.addLayout(get_slider_layout(QLabel("색상:"), self.lb_hue, self.slider_hue))
        lyt_color.addLayout(get_slider_layout(QLabel("채도:"), self.lb_saturation, self.slider_saturation))
        lyt_color.addLayout(get_slider_layout(QLabel("밝기:"), self.lb_brightness, self.slider_brightness))
        lyt_color.addLayout(get_slider_layout(QLabel("명암:"), self.lb_contrast, self.slider_contrast))
        lyt_color.addLayout(get_slider_layout(QLabel("감마:"), self.lb_gamma, self.slider_gamma))
        lyt_color.addWidget(self.btn_init_color)
        gbox_color = QGroupBox("색 조정")
        gbox_color.setLayout(lyt_color)

        wig_content = QWidget()
        lyt_content = QVBoxLayout(wig_content)
        lyt_content.addWidget(gbox_res)
        lyt_content.addWidget(gbox_expo)
        lyt_content.addWidget(gbox_WB)
        lyt_content.addWidget(gbox_BB)
        lyt_content.addWidget(gbox_color)

        self.setWidget(wig_content)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFixedWidth(260)

        self.init_view()

    def init_view(self):
        if self.camera_started:
            camera_unit: CameraUnit = self.camera_unit
            camera_unit.evtCallback.connect(self.on_event_callback)

            self.set_cmb_resolution()

            """ 노출 및 게인"""
            target_min, target_max, target_def = toupcam.TOUPCAM_AETARGET_MIN, toupcam.TOUPCAM_AETARGET_MAX, toupcam.TOUPCAM_AETARGET_DEF
            time_min, time_max, time_def = camera_unit.cam.get_ExpTimeRange()
            gain_min, gain_max, gain_def = camera_unit.cam.get_ExpoAGainRange()

            self.slider_expo_target.setRange(target_min, target_max)
            self.slider_expo_target.setValue(target_def)
            self.slider_expo_time.setRange(0, 100)
            self.slider_expo_time.setValue(time_def)
            self.slider_expo_gain.setRange(gain_min, gain_max)
            self.slider_expo_gain.setValue(gain_def)

            self.handle_expo_event()
            if camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0:
                self.handle_temp_tint_event()

            """ 화이트 밸런스 """
            self.btn_auto_WB.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            self.slider_temp.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            self.slider_tint.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            b_auto = camera_unit.cam.get_AutoExpoEnable()
            self.cb_auto_expo.setChecked(b_auto == 1)

            """ 색 조정 """
            self.set_color_text()

    """ 해상도 """

    def set_cmb_resolution(self):
        self.cmb_res.clear()
        camera_unit: CameraUnit = self.camera_unit
        if self.camera_started:
            for i in range(camera_unit.cur.model.preview):
                res = camera_unit.cur.model.res[i]
                self.cmb_res.addItem(f"{res.width}*{res.height}")
            self.cmb_res.setCurrentIndex(camera_unit.res)
        self.cmb_res.setEnabled(True)

    """ 노출 및 게인"""

    def on_auto_expo_changed(self, state):
        if self.camera_unit.set_auto_expo(state):
            self.slider_expo_target.setEnabled(state)
            self.slider_expo_time.setEnabled(not state)
            self.slider_expo_gain.setEnabled(not state)

    def on_expo_target_changed(self, value):
        if self.camera_unit.set_expo_target(value):
            self.lb_expo_target.setText(str(value))

    def on_expo_time_changed(self, slider_value):
        exposure_time = self.exponential_function.calculate_y(slider_value)
        if self.camera_unit.set_expo_time(int(exposure_time)):
            self.lb_expo_time.setText(f"{round(exposure_time / 1000, 3)}ms")

    def on_expo_gain_changed(self, value):
        if self.camera_unit.set_expo_gain(value):
            self.lb_expo_gain.setText(f"{value}%")

    """ 화이트 밸런스 """

    def on_WB_temp_changed(self, value):
        if self.camera_unit.set_white_balance_temp(value):
            self.lb_temp.setText(str(value))

    def on_WB_tint_changed(self, value):
        if self.camera_unit.set_white_balance_tint(value):
            self.lb_tint.setText(str(value))

    def init_white_balance(self):
        if self.camera_unit.init_white_balance():
            self.handle_temp_tint_event()

    """ 블랙 밸런스 """

    def on_black_balance_changed(self, color_index, value):
        if self.camera_unit.set_black_balance(color_index, value):
            if color_index == 0:
                self.lb_r.setText(str(value))
            elif color_index == 1:
                self.lb_g.setText(str(value))
            else:
                self.lb_b.setText(str(value))

    def init_black_balance(self):
        if self.camera_unit.init_black_balance():
            self.handle_black_balance_event()

    """ 색 조정 """

    def on_hue_changed(self, value):
        if self.camera_unit.set_hue(value):
            self.lb_hue.setText(str(value))

    def on_saturation_changed(self, value):
        if self.camera_unit.set_saturation(value):
            self.lb_saturation.setText(str(value))

    def on_brightness_changed(self, value):
        if self.camera_unit.set_brightness(value):
            self.lb_brightness.setText(str(value))

    def on_contrast_changed(self, value):
        if self.camera_unit.set_contrast(value):
            self.lb_contrast.setText(str(value))

    def on_gamma_changed(self, value):
        if self.camera_unit.set_gamma(value):
            self.lb_gamma.setText(str(value))

    def init_color(self):
        if self.camera_unit.init_color():
            self.set_color_text()

    def set_color_text(self):
        camera_unit: CameraUnit = self.camera_unit
        if camera_unit.cam:
            cam = camera_unit.cam
            hue = cam.get_Hue()
            saturation = cam.get_Saturation()
            brightness = cam.get_Brightness()
            contrast = cam.get_Contrast()
            gamma = cam.get_Gamma()
            self.slider_hue.setValue(hue)
            self.slider_saturation.setValue(saturation)
            self.slider_brightness.setValue(brightness)
            self.slider_contrast.setValue(contrast)
            self.slider_gamma.setValue(gamma)

    """ 이벤트 핸들러 """

    def on_event_callback(self, nEvent):
        if self.camera_unit.cam:
            if nEvent == toupcam.TOUPCAM_EVENT_EXPOSURE:
                self.handle_expo_event()
            elif nEvent == toupcam.TOUPCAM_EVENT_TEMPTINT:
                self.handle_temp_tint_event()
            elif nEvent == toupcam.TOUPCAM_EVENT_BLACK:
                self.handle_black_balance_event()

    def handle_expo_event(self):
        unit: CameraUnit = self.camera_unit
        time = unit.cam.get_ExpoTime()
        gain = unit.cam.get_ExpoAGain()
        slider_value = self.exponential_function.calculate_x(time)
        with QSignalBlocker(self.slider_expo_time):
            self.slider_expo_time.setValue(slider_value)
        with QSignalBlocker(self.slider_expo_gain):
            self.slider_expo_gain.setValue(gain)
        self.on_expo_time_changed(slider_value)
        self.on_expo_gain_changed(gain)

    def handle_temp_tint_event(self):
        unit: CameraUnit = self.camera_unit
        temp, tint = unit.cam.get_TempTint()
        self.slider_temp.setValue(temp)
        self.slider_tint.setValue(tint)

    def handle_black_balance_event(self):
        unit: CameraUnit = self.camera_unit
        rgb = unit.rgb
        self.slider_r.setValue(rgb[0])
        self.slider_g.setValue(rgb[1])
        self.slider_b.setValue(rgb[2])
