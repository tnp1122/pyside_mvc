from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout

from models import Image
from models.snapshot import Snapshot
from ui.common.camera_widget.label_camera import LabelCamera
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import MaskManagerController, MaskManagerView


class SectionCameraDisplay(QWidget):
    def __init__(self, snapshot: Snapshot, parent=None, use_mask=True, setting_visible=True, plate_border_visible=True):
        super().__init__(parent)

        self.snapshot_instance = snapshot

        self.use_mask = use_mask
        self.setting_visible = setting_visible
        self.plate_border_visible = plate_border_visible

        self.btn_switch_setting_visible = QPushButton("카메라 설정 열기")
        self.btn_set_mask_area = QPushButton("마스크 설정")
        self.btn_init_mask_area = QPushButton("마스크 영역 초기화")
        self.btn_switch_plate_border_visible = QPushButton("플레이트 영역 숨기기")
        if not self.use_mask:
            self.btn_set_mask_area.setEnabled(False)
            self.btn_init_mask_area.setEnabled(False)
            self.btn_switch_plate_border_visible.setEnabled(False)
        lyt_btn1 = QHBoxLayout()
        lyt_btn2 = QHBoxLayout()
        lyt_btn1.addWidget(self.btn_switch_setting_visible)
        lyt_btn1.addWidget(self.btn_set_mask_area)
        lyt_btn2.addWidget(self.btn_init_mask_area)
        lyt_btn = QVBoxLayout()
        lyt_btn.addLayout(lyt_btn1)
        lyt_btn.addLayout(lyt_btn2)
        lyt_btn2.addWidget(self.btn_switch_plate_border_visible)

        self.lb_camera = LabelCamera(
            snapshot=self.snapshot_instance,
            wb_roi_visible=self.setting_visible,
            plate_border_visible=self.plate_border_visible
        )
        self.wig_bottom = QWidget()
        self.lyt_bottom = QVBoxLayout(self.wig_bottom)
        self.lyt_bottom.setContentsMargins(0, 0, 0, 0)

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(4)
        lyt.addLayout(lyt_btn)
        lyt.addWidget(self.lb_camera)
        lyt.addWidget(self.wig_bottom)

        self.init_view()

    def init_view(self):
        self.set_setting_visible(self.setting_visible)

        self.btn_set_mask_area.clicked.connect(self.open_mask_manager)
        self.btn_init_mask_area.clicked.connect(self.snapshot_instance.init_plate_mask_info)
        self.btn_switch_plate_border_visible.clicked.connect(self.switch_plate_border_visible)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_label_size()

    def adjust_label_size(self):
        new_width = self.lb_camera.adjust_size()
        if new_width:
            self.setFixedWidth(new_width)

    def set_bottom_widget(self, widget: QWidget):
        self.lyt_bottom.addWidget(widget)

    def set_setting_visible(self, visible: bool):
        self.setting_visible = visible
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.set_wb_roi_visible(visible)

        if self.setting_visible:
            self.btn_switch_setting_visible.setText("카메라 설정 숨기기")
        else:
            self.btn_switch_setting_visible.setText("카메라 설정 열기")

    def switch_plate_border_visible(self):
        self.plate_border_visible = not self.plate_border_visible
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.set_plate_border_visible(self.plate_border_visible)

        if self.plate_border_visible:
            self.btn_switch_plate_border_visible.setText("플레이트 영역 숨기기")
        else:
            self.btn_switch_plate_border_visible.setText("플레이트 영역 보기")

    def open_mask_manager(self):
        lb_camera: LabelCamera = self.lb_camera
        if lb_camera.image is not None:
            snapshot: Snapshot = lb_camera.snapshot_instance
            snapshot.change_origin_image(Image(lb_camera.image))
            mask_manager = MaskManagerController(snapshot=snapshot)
            manager_view: MaskManagerView = mask_manager.view
            manager_view.on_select_changed(1)
            manager_view.view_radio.set_visibility(0, False)
            manager_view.view_radio.set_visibility(2, False)
            mask_manager.view.exec()

    def update_wb_roi(self, x, y, width, height):
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.update_wb_roi(x, y, width, height)

    def take_snapshot(self):
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.take_snapshot()

    def set_sensor_indexes(self, indexes: list, colors: list):
        lb_camera: LabelCamera = self.lb_camera
        lb_camera.set_sensor_indexes(indexes, colors)
