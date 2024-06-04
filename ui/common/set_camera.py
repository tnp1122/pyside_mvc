import numpy as np
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtWidgets import QScrollArea, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, QLabel, QSlider, \
    QPushButton, QWidget, QSizePolicy, QLayout, QButtonGroup, QRadioButton

from ui.common import ImageButton
from util.camera_manager import CameraUnit, toupcam
from util import local_storage_manager as lsm


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


class ButtonTitle(QPushButton):
    def __init__(self, title="", *args, **kwargs):
        super().__init__(*args, **kwargs)

        lb_title = QLabel(title)
        img_arrow = lsm.get_static_image_path("expand_arrow.png")
        self.btn_expand = ImageButton(img_arrow)

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(4, 0, 4, 0)
        lyt.addWidget(lb_title)
        lyt.addStretch()
        lyt.addWidget(self.btn_expand)

        self.setFixedHeight(24)
        self.set_style_sheet()
        self.rotate_arrow(True)

    def set_style_sheet(self):
        self.setObjectName("ButtonTitle")
        style = f"""
            #ButtonTitle {{
                background-color: lightgray;
                border: none;
                border-radius: 1px;
            }}
        """
        self.setStyleSheet(style)

    def rotate_arrow(self, upper):
        if upper:
            self.btn_expand.rotate_icon(0)
        else:
            self.btn_expand.rotate_icon(180)


class GroupBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)

        self.wig_title = ButtonTitle(title)
        self.wig_title.clicked.connect(self.toggle)
        self.wig_title.btn_expand.clicked.connect(self.toggle)
        self.wig_content = QWidget()

        self.pane = QWidget()
        self.lyt = QVBoxLayout(self.pane)
        self.lyt.setContentsMargins(0, 0, 0, 0)
        self.lyt.addWidget(self.wig_title)
        self.lyt.addWidget(self.wig_content)

        lyt_main = QVBoxLayout(self)
        lyt_main.setContentsMargins(0, 0, 0, 0)
        lyt_main.addWidget(self.pane)

        self.set_style_sheet()

    def set_style_sheet(self):
        self.pane.setObjectName("Group")
        style = f"""
            QWidget#Group {{
                background-color: white;
                border: none;
            }}
        """
        self.pane.setStyleSheet(style)

    def set_content(self, content: QLayout):
        self.wig_content.setLayout(content)

    def toggle(self):
        content: QWidget = self.wig_content
        content.setVisible(not content.isVisible())
        self.wig_title.rotate_arrow(content.isVisible())


class SetCamera(QScrollArea):
    camera_unit = CameraUnit()

    def __init__(self, parent=None):
        super().__init__(parent)

        camera_unit: CameraUnit = self.camera_unit
        time_min, time_max, _ = camera_unit.cam.get_ExpTimeRange()
        self.exponential_function = ExponentialFunction(0, time_min, 100, time_max)
        self.camera_started = camera_unit.pData is not None

        """ 플랫 필드 보정 """
        self.cb_ffc = QCheckBox("활성화")
        self.cb_ffc.setEnabled(False)
        self.cb_ffc.stateChanged.connect(self.on_cb_ffc_changed)
        self.btn_capture_ffc_bg = QPushButton("배경 캡처")
        self.btn_capture_ffc_bg.clicked.connect(self.on_btn_ffc_clicked)
        lyt_ffc = QVBoxLayout()
        lyt_ffc.addWidget(self.cb_ffc)
        lyt_ffc.addWidget(self.btn_capture_ffc_bg)
        gbox_ffc = GroupBox("플랫 필드 보정")
        gbox_ffc.set_content(lyt_ffc)

        """ 해상도 """
        self.cmb_res = QComboBox()
        self.cmb_res.setEnabled(False)
        lyt_res = QVBoxLayout()
        lyt_res.addWidget(self.cmb_res)
        gbox_res = GroupBox("해상도")
        gbox_res.set_content(lyt_res)
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
        gbox_expo = GroupBox("노출 및 게인")
        gbox_expo.set_content(lyt_expo)
        self.cb_auto_expo.stateChanged.connect(self.on_auto_expo_changed)
        self.slider_expo_target.valueChanged.connect(self.on_expo_target_changed)
        self.slider_expo_time.valueChanged.connect(self.on_expo_time_changed)
        self.slider_expo_gain.valueChanged.connect(self.on_expo_gain_changed)

        """ 화이트 밸런스 """
        ## 온도 색조 모드
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
        self.slider_temp.valueChanged.connect(self.on_wb_temp_changed)
        self.slider_tint.valueChanged.connect(self.on_wb_tint_changed)
        self.wig_wb_temp_tint = QWidget()
        lyt_wb_temp_tint = QVBoxLayout(self.wig_wb_temp_tint)
        lyt_wb_temp_tint.setContentsMargins(0, 0, 0, 0)
        lyt_wb_temp_tint.addLayout(get_slider_layout(QLabel("색 온도:"), self.lb_temp, self.slider_temp))
        lyt_wb_temp_tint.addLayout(get_slider_layout(QLabel("색조:"), self.lb_tint, self.slider_tint))
        # ## rgb 게인 모드
        # wb_gain_def = toupcam.TOUPCAM_WBGAIN_DEF
        # wb_gain_min = toupcam.TOUPCAM_WBGAIN_MIN
        # wb_gain_max = toupcam.TOUPCAM_WBGAIN_MAX
        # self.lb_r_wb = QLabel(str(wb_gain_def))
        # self.lb_g_wb = QLabel(str(wb_gain_def))
        # self.lb_b_wb = QLabel(str(wb_gain_def))
        # self.slider_r_wb = QSlider(Qt.Horizontal)
        # self.slider_g_wb = QSlider(Qt.Horizontal)
        # self.slider_b_wb = QSlider(Qt.Horizontal)
        # self.slider_r_wb.setRange(wb_gain_min, wb_gain_max)
        # self.slider_g_wb.setRange(wb_gain_min, wb_gain_max)
        # self.slider_b_wb.setRange(wb_gain_min, wb_gain_max)
        # self.slider_r_wb.setValue(wb_gain_def)
        # self.slider_g_wb.setValue(wb_gain_def)
        # self.slider_b_wb.setValue(wb_gain_def)
        # self.slider_r_wb.setEnabled(self.camera_started)
        # self.slider_g_wb.setEnabled(self.camera_started)
        # self.slider_b_wb.setEnabled(self.camera_started)
        # self.slider_r_wb.valueChanged.connect(lambda value: self.on_wb_gain_changed(0, value))
        # self.slider_g_wb.valueChanged.connect(lambda value: self.on_wb_gain_changed(1, value))
        # self.slider_b_wb.valueChanged.connect(lambda value: self.on_wb_gain_changed(2, value))
        # self.wig_wb_gain = QWidget()
        # lyt_wb_gain = QVBoxLayout(self.wig_wb_gain)
        # lyt_wb_gain.setContentsMargins(0, 0, 0, 0)
        # lyt_wb_gain.addLayout(get_slider_layout(QLabel("빨강:"), self.lb_r_wb, self.slider_r_wb))
        # lyt_wb_gain.addLayout(get_slider_layout(QLabel("초록:"), self.lb_g_wb, self.slider_g_wb))
        # lyt_wb_gain.addLayout(get_slider_layout(QLabel("파랑:"), self.lb_b_wb, self.slider_b_wb))
        ## 공통
        # rb_wb_mode_group = QButtonGroup()
        # self.rb_wb_temp_tint = QRadioButton("색 온도 색조 모드")
        # self.rb_wb_gain = QRadioButton("rgb 게인 모드")
        # rb_wb_mode_group.addButton(self.rb_wb_temp_tint)
        # rb_wb_mode_group.addButton(self.rb_wb_gain)
        # lyt_rb_wb_mode = QHBoxLayout()
        # lyt_rb_wb_mode.setContentsMargins(0, 0, 0, 0)
        # lyt_rb_wb_mode.addWidget(self.rb_wb_temp_tint)
        # lyt_rb_wb_mode.addWidget(self.rb_wb_gain)
        self.btn_auto_wb = QPushButton("화이트 밸런스")
        self.btn_auto_wb.setEnabled(self.camera_started)
        self.btn_auto_wb.clicked.connect(self.camera_unit.auto_white_balance_once)
        self.btn_init_wb = QPushButton("기본값")
        self.btn_init_wb.setEnabled(self.camera_started)
        self.btn_init_wb.clicked.connect(self.init_white_balance)
        lyt_wb = QVBoxLayout()
        # lyt_wb.addLayout(lyt_rb_wb_mode)
        lyt_wb.addWidget(self.wig_wb_temp_tint)
        # lyt_wb.addWidget(self.wig_wb_gain)
        lyt_wb.addLayout(get_twin_button_layout(self.btn_auto_wb, self.btn_init_wb))
        gbox_wb = GroupBox("화이트 밸런스")
        gbox_wb.set_content(lyt_wb)

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
        self.btn_auto_bb = QPushButton("블랙 밸런스")
        self.btn_auto_bb.setEnabled(self.camera_started)
        self.btn_auto_bb.clicked.connect(self.camera_unit.auto_black_blance_once)
        self.btn_init_bb = QPushButton("기본값")
        self.btn_init_bb.setEnabled(self.camera_started)
        self.btn_init_bb.clicked.connect(self.init_black_balance)
        lyt_bb = QVBoxLayout()
        lyt_bb.addLayout(get_slider_layout(QLabel("빨강:"), self.lb_r, self.slider_r))
        lyt_bb.addLayout(get_slider_layout(QLabel("녹색:"), self.lb_g, self.slider_g))
        lyt_bb.addLayout(get_slider_layout(QLabel("파랑:"), self.lb_b, self.slider_b))
        lyt_bb.addLayout(get_twin_button_layout(self.btn_auto_bb, self.btn_init_bb))
        gbox_bb = GroupBox("블랙 밸런스")
        gbox_bb.set_content(lyt_bb)

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
        gbox_color = GroupBox("색 조정")
        gbox_color.set_content(lyt_color)

        """ 광원 주파수(Anti-flicker) """
        self.rb_hz_1 = QRadioButton("교류 전류(50Hz)")
        self.rb_hz_0 = QRadioButton("교류 전류(60Hz)")
        self.rb_hz_2 = QRadioButton("직류(DC)")
        self.rb_group_hz = QButtonGroup(self)
        self.rb_group_hz.addButton(self.rb_hz_0, 0)
        self.rb_group_hz.addButton(self.rb_hz_1, 1)
        self.rb_group_hz.addButton(self.rb_hz_2, 2)
        self.rb_group_hz.buttonClicked.connect(self.on_rb_hz_changed)
        lyt_hz = QVBoxLayout()
        lyt_hz.addWidget(self.rb_hz_0)
        lyt_hz.addWidget(self.rb_hz_1)
        lyt_hz.addWidget(self.rb_hz_2)
        gbox_hz = GroupBox("광원 주파수(Anti-flicker)")
        gbox_hz.set_content(lyt_hz)

        """ 전체 레이아웃 """
        wig_content = QWidget()
        lyt_content = QVBoxLayout(wig_content)
        lyt_content.setContentsMargins(2, 2, 2, 2)
        lyt_content.addWidget(gbox_ffc)
        lyt_content.addWidget(gbox_res)
        lyt_content.addWidget(gbox_expo)
        lyt_content.addWidget(gbox_wb)
        lyt_content.addWidget(gbox_bb)
        lyt_content.addWidget(gbox_color)
        lyt_content.addWidget(gbox_hz)
        lyt_content.addStretch()

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

            """ 해상도 """

            self.set_cmb_resolution()

            """ 노출 및 게인"""
            b_auto = camera_unit.cam.get_AutoExpoEnable()
            self.cb_auto_expo.setChecked(b_auto == 1)

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
            self.btn_auto_wb.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            self.slider_temp.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            self.slider_tint.setEnabled(camera_unit.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            # self.handle_white_balance_gain_event()
            # self.update_white_balance_gain()

            """ 색 조정 """
            self.set_color_text()

            """ 광원 주파수(Anti-flicker) """
            hz = camera_unit.cam.get_HZ()
            if hz == 0:
                self.rb_hz_0.setChecked(True)
            elif hz == 1:
                self.rb_hz_1.setChecked(True)
            else:
                self.rb_hz_2.setChecked(True)

    """ 플랫 필드 보정 """
    def on_cb_ffc_changed(self):
        camera_unit: CameraUnit = self.camera_unit
        if self.cb_ffc.isChecked():
            camera_unit.cam.put_Option(toupcam.TOUPCAM_OPTION_FFC, 1)
        else:
            camera_unit.cam.put_Option(toupcam.TOUPCAM_OPTION_FFC, 0)

    def on_btn_ffc_clicked(self):
        self.camera_unit.cam.FfcOnce()
        self.cb_ffc.setEnabled(True)

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

    def on_wb_temp_changed(self, value):
        if self.camera_unit.set_white_balance_temp(value):
            self.lb_temp.setText(str(value))
        # self.update_white_balance_gain()

    def on_wb_tint_changed(self, value):
        if self.camera_unit.set_white_balance_tint(value):
            self.lb_tint.setText(str(value))

    #     self.update_white_balance_gain()
    #
    # def on_wb_gain_changed(self, color_index, value):
    #     rgb = list(self.camera_unit.get_white_balance_gain())
    #     rgb[color_index] = value
    #     print(f"[on wb gain changed] rgb: {rgb}")
    #     if self.camera_unit.set_white_balance_gain(rgb):
    #         if color_index == 0:
    #             self.lb_r_wb.setText(str(value))
    #         elif color_index == 1:
    #             self.lb_g_wb.setText(str(value))
    #         else:
    #             self.lb_b_wb.setText(str(value))
    #
    # def update_white_balance_gain(self):
    #     unit: CameraUnit = self.camera_unit
    #     gain = unit.get_white_balance_gain()
    #     print(f"[handle wb gain] gain: {gain}")
    #     self.slider_r_wb.setValue(gain[0])
    #     self.slider_g_wb.setValue(gain[1])
    #     self.slider_b_wb.setValue(gain[2])

    def init_white_balance(self):
        if self.camera_unit.init_white_balance():
            self.handle_temp_tint_event()
            # self.handle_white_balance_gain_event()

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

    """ 광원 주파수(Anti-flicker) """

    def on_rb_hz_changed(self, button):
        button_id = self.rb_group_hz.id(button)
        self.camera_unit.cam.put_HZ(button_id)

    """ 이벤트 핸들러 """

    def on_event_callback(self, nEvent):
        if self.camera_unit.cam:
            if nEvent == toupcam.TOUPCAM_EVENT_EXPOSURE:
                self.handle_expo_event()
            elif nEvent == toupcam.TOUPCAM_EVENT_TEMPTINT:
                self.handle_temp_tint_event()
            # elif nEvent == toupcam.TOUPCAM_EVENT_WBGAIN:
            #     self.handle_white_balance_gain_event()
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
        # self.update_white_balance_gain()

    # def handle_white_balance_gain_event(self):
    #     unit: CameraUnit = self.camera_unit
    #     gain = unit.get_white_balance_gain()
    #     print(f"[handler wb gain] gain: {gain}")
    #     # with QSignalBlocker(self.slider_r_wb):
    #     self.slider_r_wb.setValue(gain[0])
    #     # with QSignalBlocker(self.slider_g_wb):
    #     self.slider_g_wb.setValue(gain[1])
    #     # with QSignalBlocker(self.slider_b_wb):
    #     self.slider_b_wb.setValue(gain[2])

    def handle_black_balance_event(self):
        unit: CameraUnit = self.camera_unit
        rgb = unit.rgb
        self.slider_r.setValue(rgb[0])
        self.slider_g.setValue(rgb[1])
        self.slider_b.setValue(rgb[2])
