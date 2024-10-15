import numpy as np
from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QLineEdit, QFrame

from models.snapshot import Snapshot
from ui.common.camera_widget.camera_widget_status import CameraWidgetStatus
from ui.common.camera_widget.label_camera import LabelCamera
from ui.common.camera_widget.section_set_camera import GroupBox
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import MaskManagerController, MaskManagerView
from util.enums import LabCorrectionType


class SectionCameraDisplay(QWidget):
    lab_correction_factors_set_signal = Signal(np.ndarray)

    def __init__(self, status: CameraWidgetStatus, parent=None):
        super().__init__(parent)

        self.status = status
        self.block_time = 500
        self.block_cb_whole_roi = False
        self.block_cb_manual_roi = False

        """ 디스플레이 설정 """
        self.btn_switch_setting_visible = QPushButton("카메라 설정 열기")
        self.btn_set_mask_area = QPushButton("마스크 설정")
        self.btn_init_mask_area = QPushButton("마스크 영역 초기화")
        self.btn_switch_plate_border_visible = QPushButton("플레이트 영역 숨기기")
        if not self.status.use_mask:
            self.btn_set_mask_area.setEnabled(False)
            self.btn_init_mask_area.setEnabled(False)
            self.btn_switch_plate_border_visible.setEnabled(False)
        lyt_btn1 = QHBoxLayout()
        lyt_btn2 = QHBoxLayout()
        lyt_btn1.addWidget(self.btn_switch_setting_visible)
        lyt_btn1.addWidget(self.btn_set_mask_area)
        lyt_btn2.addWidget(self.btn_init_mask_area)
        lyt_btn2.addWidget(self.btn_switch_plate_border_visible)
        lyt_basic_setting = QVBoxLayout()
        lyt_basic_setting.addLayout(lyt_btn1)
        lyt_basic_setting.addLayout(lyt_btn2)
        gbox_basic_setting = GroupBox("기본 설정")
        gbox_basic_setting.set_content(lyt_basic_setting)

        """ Lab 보정 관련 """
        self.cb_lab_whole_roi = QCheckBox("전체 영역 평균")
        self.cb_lab_manual_roi = QCheckBox("ROI 직접 선택")
        self.cb_lab_manual_color = QCheckBox("기준색 직접 지정")
        lyt_cb_lab = QVBoxLayout()
        lyt_cb_lab.addWidget(self.cb_lab_whole_roi)
        lyt_cb_lab.addWidget(self.cb_lab_manual_roi)
        lyt_cb_lab.addWidget(self.cb_lab_manual_color)
        divider_lab = QFrame()
        divider_lab.setFrameShape(QFrame.VLine)
        divider_lab.setFrameShadow(QFrame.Sunken)
        lb_reference_rgb_r = QLabel("R")
        lb_reference_rgb_g = QLabel("G")
        lb_reference_rgb_b = QLabel("B")
        lb_reference_lab_l = QLabel("L")
        lb_reference_lab_a = QLabel("a")
        lb_reference_lab_b = QLabel("b")
        self.et_reference_rgb_r = QLineEdit("255")
        self.et_reference_rgb_g = QLineEdit("255")
        self.et_reference_rgb_b = QLineEdit("255")
        self.et_reference_lab_l = QLineEdit("100")
        self.et_reference_lab_a = QLineEdit("100")
        self.et_reference_lab_b = QLineEdit("100")
        lyt_reference_rgb = QHBoxLayout()
        lyt_reference_rgb.addWidget(lb_reference_rgb_r)
        lyt_reference_rgb.addWidget(self.et_reference_rgb_r)
        lyt_reference_rgb.addWidget(lb_reference_rgb_g)
        lyt_reference_rgb.addWidget(self.et_reference_rgb_g)
        lyt_reference_rgb.addWidget(lb_reference_rgb_b)
        lyt_reference_rgb.addWidget(self.et_reference_rgb_b)
        lyt_reference_lab = QHBoxLayout()
        lyt_reference_lab.addWidget(lb_reference_lab_l)
        lyt_reference_lab.addWidget(self.et_reference_lab_l)
        lyt_reference_lab.addWidget(lb_reference_lab_a)
        lyt_reference_lab.addWidget(self.et_reference_lab_a)
        lyt_reference_lab.addWidget(lb_reference_lab_b)
        lyt_reference_lab.addWidget(self.et_reference_lab_b)
        self.btn_save_reference_color = QPushButton("기준값 저장")
        self.btn_undo_reference_color_change = QPushButton("되돌리기")
        self.btn_undo_reference_color_change.setEnabled(False)
        lyt_btn_reference_color = QHBoxLayout()
        lyt_btn_reference_color.addWidget(self.btn_save_reference_color)
        lyt_btn_reference_color.addWidget(self.btn_undo_reference_color_change)
        lyt_input_reference_color = QVBoxLayout()
        lyt_input_reference_color.addLayout(lyt_reference_rgb)
        lyt_input_reference_color.addLayout(lyt_reference_lab)
        lyt_input_reference_color.addLayout(lyt_btn_reference_color)

        lyt_cb_lab.setContentsMargins(0, 8, 0, 8)
        lyt_input_reference_color.setContentsMargins(0, 8, 0, 8)
        lyt_lab_setting = QHBoxLayout()
        lyt_lab_setting.setContentsMargins(12, 0, 12, 0)
        lyt_lab_setting.addLayout(lyt_cb_lab)
        lyt_lab_setting.addWidget(divider_lab)
        lyt_lab_setting.addLayout(lyt_input_reference_color)
        self.gbox_lab_setting = GroupBox("Lab 보정")
        self.gbox_lab_setting.set_content(lyt_lab_setting)

        """ 카메라 라벨 """
        self.lb_camera = LabelCamera(self.status)
        self.wig_bottom = QWidget()
        self.lyt_bottom = QVBoxLayout(self.wig_bottom)
        self.lyt_bottom.setContentsMargins(0, 0, 0, 0)

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(4)
        # lyt.addLayout(lyt_btn)
        lyt.addWidget(gbox_basic_setting)
        lyt.addWidget(self.gbox_lab_setting)
        lyt.addWidget(self.lb_camera)
        lyt.addWidget(self.wig_bottom)

        self.init_view()

    def init_view(self):
        self.update_setting_visible()
        self.update_plate_border_visible()
        # self.update_lab_correction_type()
        self.lb_camera.snapshot_initialized_signal.connect(self.update_lab_correction_type)

        self.btn_set_mask_area.clicked.connect(self.open_mask_manager)
        self.btn_init_mask_area.clicked.connect(self.status.snapshot_instance.init_plate_mask_info)
        self.btn_switch_plate_border_visible.clicked.connect(self.on_btn_switch_plate_border_visible_clicked)

        self.gbox_lab_setting.toggled.connect(self.on_gbox_lab_setting_toggled)
        self.cb_lab_whole_roi.clicked.connect(self.on_cb_lab_whole_roi_checked)
        self.cb_lab_manual_roi.clicked.connect(self.on_cb_lab_manual_roi_checked)
        self.cb_lab_manual_color.clicked.connect(self.on_cb_lab_manual_color_checked)
        self.et_reference_rgb_r.textEdited.connect(lambda value: self.on_et_reference_rgb_changed("r", value))
        self.et_reference_rgb_g.textEdited.connect(lambda value: self.on_et_reference_rgb_changed("g", value))
        self.et_reference_rgb_b.textEdited.connect(lambda value: self.on_et_reference_rgb_changed("b", value))
        self.et_reference_lab_l.textEdited.connect(lambda value: self.on_et_reference_lab_changed("l", value))
        self.et_reference_lab_a.textEdited.connect(lambda value: self.on_et_reference_lab_changed("a", value))
        self.et_reference_lab_b.textEdited.connect(lambda value: self.on_et_reference_lab_changed("b", value))
        self.btn_save_reference_color.clicked.connect(self.on_btn_save_reference_color_clicked)

        self.status.lab_correction_type_changed.connect(self.update_lab_correction_type)
        self.status.lab_reference_rgb_changed.connect(self.update_et_reference_rgb)
        self.status.lab_reference_lab_changed.connect(self.update_et_reference_lab)
        # self.status.lab_standard_rgb_changed.connect(self.update_lab_stand_color_et)
        # self.status.lab_standard_lab_changed.connect(self.update_lab_stand_color_et)
        self.status.lab_reference_hole_index_changed.connect(self.on_change_lab_reference_hole_index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_label_size()

    def adjust_label_size(self):
        new_width = self.lb_camera.adjust_size()
        if new_width:
            self.setFixedWidth(new_width)

    def release_cb_whole_roi(self):
        self.block_cb_whole_roi = False

    def release_cb_manual_roi(self):
        self.block_cb_manual_roi = False

    def set_bottom_widget(self, widget: QWidget):
        self.lyt_bottom.addWidget(widget)

    def open_mask_manager(self):
        lb_camera: LabelCamera = self.lb_camera
        if lb_camera.image is not None:
            # snapshot: Snapshot = self.status.snapshot_instance
            # snapshot.change_origin_image(Image(lb_camera.image))
            snapshot = self.take_snapshot()
            mask_manager = MaskManagerController(snapshot=snapshot)
            manager_view: MaskManagerView = mask_manager.view
            manager_view.on_select_changed(1)
            manager_view.view_radio.set_visibility(0, False)
            manager_view.view_radio.set_visibility(2, False)
            mask_manager.view.exec()

    def take_snapshot(self) -> Snapshot:
        lb_camera: LabelCamera = self.lb_camera
        return lb_camera.take_snapshot()

    def set_sensor_indexes(self, indexes: list, colors: list):
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.set_sensor_indexes(indexes, colors)

    def update_setting_visible(self):
        visible = self.status.setting_visible
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.refresh_paint()

        if visible:
            self.btn_switch_setting_visible.setText("카메라 설정 숨기기")
        else:
            self.btn_switch_setting_visible.setText("카메라 설정 열기")

    def update_plate_border_visible(self):
        # visible = self.status.plate_border_visible
        visible = self.status.switch_plate_border_visible()

        if visible:
            self.btn_switch_plate_border_visible.setText("플레이트 영역 숨기기")
        else:
            self.btn_switch_plate_border_visible.setText("플레이트 영역 보기")

    def update_lab_correction_type(self):
        if self.block_cb_whole_roi or self.block_cb_manual_roi:  # or self.block_cb_manual_color:
            return
        snapshot = self.take_snapshot()
        self.cb_lab_whole_roi.setChecked(False)
        self.cb_lab_manual_roi.setChecked(False)
        self.cb_lab_manual_color.setChecked(False)
        lab_correction_type = self.status.lab_correction_type
        if lab_correction_type == LabCorrectionType.WHOLE_HALL_ROI:
            self.block_cb_whole_roi = True
            QTimer.singleShot(self.block_time, self.release_cb_whole_roi)
            self.cb_lab_whole_roi.setChecked(True)

            # r, g, b = snapshot.average_of_mean_colors
            l, a, b = snapshot.average_lab_of_mean_colors
            self.status.set_lab_correction_reference_lab(l, a, b)
        elif lab_correction_type == LabCorrectionType.SINGLE_HALL_ROI:
            self.block_cb_manual_roi = True
            QTimer.singleShot(self.block_time, self.release_cb_manual_roi)
            self.cb_lab_manual_roi.setChecked(True)

            r, g, b = snapshot.get_mean_color_of_roi(self.status.get_lab_correction_reference_hole_index())
            self.status.set_lab_correction_reference_rgb(r, g, b)
        else:
            self.cb_lab_manual_color.setChecked(True)

    def on_change_lab_reference_hole_index(self, index: int):
        snapshot = self.take_snapshot()
        r, g, b = snapshot.get_mean_color_of_roi(index)
        self.status.set_lab_correction_reference_rgb(r, g, b)

    def update_et_reference_rgb(self):
        r, g, b = self.status.lab_correction_reference_rgb
        self.et_reference_rgb_r.setText(f"{r:.4f}")
        self.et_reference_rgb_g.setText(f"{g:.4f}")
        self.et_reference_rgb_b.setText(f"{b:.4f}")

    def update_et_reference_lab(self):
        l, a, b = self.status.lab_correction_reference_lab
        self.et_reference_lab_l.setText(f"{l:.4f}")
        self.et_reference_lab_a.setText(f"{a:.4f}")
        self.et_reference_lab_b.setText(f"{b:.4f}")

    def on_btn_switch_plate_border_visible_clicked(self):
        self.update_plate_border_visible()
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.refresh_paint()

    def on_gbox_lab_setting_toggled(self, toggled: bool):
        self.status.set_lab_roi_visible(toggled)

    def on_cb_lab_whole_roi_checked(self):
        self.status.set_lab_correction_type(LabCorrectionType.WHOLE_HALL_ROI)
        self.update_lab_correction_type()

    def on_cb_lab_manual_roi_checked(self):
        self.status.set_lab_correction_type(LabCorrectionType.SINGLE_HALL_ROI)
        self.update_lab_correction_type()

    def on_cb_lab_manual_color_checked(self):
        self.status.set_lab_correction_type(LabCorrectionType.MANUAL_COLOR)
        self.update_lab_correction_type()

    def on_et_reference_rgb_changed(self, color: str, value: float):
        if self.status.lab_correction_type != LabCorrectionType.MANUAL_COLOR:
            self.status.set_lab_correction_type(LabCorrectionType.MANUAL_COLOR)
        v = float(value)
        if 0 <= v <= 255:
            kwargs = {color: v}
            self.status.set_lab_correction_reference_rgb(**kwargs)

    def on_et_reference_lab_changed(self, component: str, value: float):
        if self.status.lab_correction_type != LabCorrectionType.MANUAL_COLOR:
            self.status.set_lab_correction_type(LabCorrectionType.MANUAL_COLOR)
        v = float(value)
        if component == 'l' and 0 <= v <= 100:
            self.status.set_lab_correction_reference_lab(l=v)
        elif component in ['a', 'b'] and -128 <= v <= 128:
            kwargs = {component: v}
            self.status.set_lab_correction_reference_lab(**kwargs)

    def on_btn_save_reference_color_clicked(self):
        ref_l, ref_a, ref_b = self.status.lab_correction_reference_lab
        factors = self.status.snapshot_instance.set_lab_correction_factors(ref_l, ref_a, ref_b)
        self.lab_correction_factors_set_signal.emit(factors)

    def update_wb_roi(self, x, y, width, height):
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.update_wb_roi(x, y, width, height)
