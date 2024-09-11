import logging

import numpy as np
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy

from models import Image
from models.snapshot import Snapshot
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import MaskManagerController, MaskManagerView
from util import image_converter as ic
from util.camera_manager import CameraUnit, toupcam


class CameraViewer(QWidget):
    camera_unit = CameraUnit()
    snapshot_initialized_signal = Signal()

    def __init__(self, parent=None, use_mask=True, setting_visible=True, mask_border_visible=True):
        super().__init__(parent)

        self.use_mask = use_mask
        self.setting_visible = setting_visible
        self.mask_border_visible = mask_border_visible
        self.lb_initialized = False
        self.snapshot_initialized = False

        self.image = None
        self.snapshot_instance = Snapshot()
        self.sensor_indexes = []
        self.sensor_colors = []
        self.wb_x, self.wb_y, self.wb_width, self.wb_height = None, None, None, None

        self.btn_switch_setting_visible = QPushButton("카메라 설정 열기")
        self.btn_set_mask_area = QPushButton("마스크 설정")
        self.btn_init_mask_area = QPushButton("마스크 영역 초기화")
        self.btn_switch_mask_border_visible = QPushButton("플레이트 영역 숨기기")
        if not self.use_mask:
            self.btn_set_mask_area.setEnabled(False)
            self.btn_init_mask_area.setEnabled(False)
            self.btn_switch_mask_border_visible.setEnabled(False)
        lyt_btn1 = QHBoxLayout()
        lyt_btn2 = QHBoxLayout()
        lyt_btn1.addWidget(self.btn_switch_setting_visible)
        lyt_btn1.addWidget(self.btn_set_mask_area)
        lyt_btn2.addWidget(self.btn_init_mask_area)
        lyt_btn = QVBoxLayout()
        lyt_btn.addLayout(lyt_btn1)
        lyt_btn.addLayout(lyt_btn2)
        lyt_btn2.addWidget(self.btn_switch_mask_border_visible)

        self.lb_image = QLabel("No Image")
        self.lb_image.setStyleSheet("border: 1px solid black")
        self.lb_image.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.wig_bottom = QWidget()
        self.lyt_bottom = QVBoxLayout(self.wig_bottom)
        self.lyt_bottom.setContentsMargins(0, 0, 0, 0)

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(4)
        lyt.addLayout(lyt_btn)
        lyt.addWidget(self.lb_image)
        lyt.addWidget(self.wig_bottom)

        self.init_view()

    def init_view(self):
        self.camera_unit.evtCallback.connect(self.on_event_callback)
        self.camera_unit.signal_image.connect(self.update_image)

        self.switch_btn_setting_visible(self.setting_visible)

        self.btn_set_mask_area.clicked.connect(self.open_mask_manager)
        self.btn_init_mask_area.clicked.connect(self.snapshot_instance.init_plate_mask_info)
        self.btn_switch_mask_border_visible.clicked.connect(self.switch_mask_border_visible)

    def on_event_callback(self, nEvent):
        if self.camera_unit.cam:
            if nEvent == toupcam.TOUPCAM_EVENT_ERROR:
                self.camera_unit.close_camera()
                logging.error("Generic Error.: 카메라 상태를 확인하세요.")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_label_size()

    def update_image(self, image: np.ndarray):
        if image is not None:
            self.image = image
            pixmap = ic.array_to_q_pixmap(image, True)

            self.paint_wb_roi(pixmap)
            self.paint_plate_border(pixmap)

            self.lb_image.setPixmap(pixmap.scaled(self.lb_image.size(), Qt.KeepAspectRatio))

            if not self.lb_initialized:
                self.adjust_label_size()
                self.lb_initialized = True

            if not self.snapshot_initialized:
                snapshot: Snapshot = self.snapshot_instance
                snapshot.init_origin_image(Image(image))
                snapshot.mask.set_flare_threshold(255)
                self.snapshot_initialized = True
                self.snapshot_initialized_signal.emit()

    def adjust_label_size(self):
        pixmap = self.lb_image.pixmap()
        if not pixmap:
            return

        img_width = pixmap.width()
        img_height = pixmap.height()
        label_height = self.lb_image.height()

        new_width = int(label_height * img_width / img_height)
        self.lb_image.setFixedWidth(new_width)
        self.setFixedWidth(self.lb_image.width())

    def paint_wb_roi(self, pixmap: QPixmap):
        if self.wb_x is None or not self.setting_visible:
            return

        rect = QRect(self.wb_x, self.wb_y, self.wb_width, self.wb_height)
        text = "화이트 밸런스"
        text_rect = QRect(self.wb_x, self.wb_y - 40, 200, 40)
        font = QFont("Malgun Gothic", 22)
        font.setBold(True)

        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 5))
        painter.setFont(font)

        painter.drawRect(rect)
        painter.drawText(text_rect, Qt.AlignLeft, text)
        painter.end()

    def paint_plate_border(self, pixmap: QPixmap):
        if not self.mask_border_visible:
            return

        snapshot: Snapshot = self.snapshot_instance

        x, y, width, height = snapshot.plate_position.get_crop_area()
        r = snapshot.mask.radius
        row_axes = snapshot.plate_position.rows
        column_axes = snapshot.plate_position.columns

        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 5))
        painter.drawRect(x, y, width, height)
        for i, idx in enumerate(self.sensor_indexes):
            painter.setPen(QPen(self.sensor_colors[i], 5))
            solvent_idx, additive_idx = divmod(idx, 8)
            if snapshot.plate_position.direction == 0:
                sensor_x = x + column_axes[solvent_idx]
                sensor_y = y + row_axes[additive_idx]
            else:
                sensor_x = x + column_axes[additive_idx]
                sensor_y = y + row_axes[abs(solvent_idx - 11)]

            painter.drawEllipse(sensor_x - r, sensor_y - r, r * 2, r * 2)
        painter.end()

    def update_wb_roi(self, x, y, width, height):
        self.wb_x, self.wb_y, self.wb_width, self.wb_height = x, y, width, height
        self.update_image(self.image)

    def switch_btn_setting_visible(self, visible: bool):
        self.setting_visible = visible
        if self.setting_visible:
            self.btn_switch_setting_visible.setText("카메라 설정 숨기기")
        else:
            self.btn_switch_setting_visible.setText("카메라 설정 열기")

    def set_bottom_widget(self, widget: QWidget):
        self.lyt_bottom.addWidget(widget)

    def open_mask_manager(self):
        if self.image is not None:
            snapshot: Snapshot = self.snapshot_instance
            snapshot.change_origin_image(Image(self.image))
            mask_manager = MaskManagerController(snapshot=self.snapshot_instance)
            manager_view: MaskManagerView = mask_manager.view
            manager_view.on_select_changed(1)
            manager_view.view_radio.set_visibility(0, False)
            manager_view.view_radio.set_visibility(2, False)
            mask_manager.view.exec()

    def switch_mask_border_visible(self):
        self.mask_border_visible = not self.mask_border_visible

        if self.mask_border_visible:
            self.btn_switch_mask_border_visible.setText("플레이트 영역 숨기기")
        else:
            self.btn_switch_mask_border_visible.setText("플레이트 영역 보기")

    def take_snapshot(self):
        if self.image is not None:
            snapshot: Snapshot = self.snapshot_instance
            snapshot.change_origin_image(Image(self.image))

    def set_sensor_indexes(self, indexes: list, colors: list):
        self.sensor_indexes = indexes
        self.sensor_colors = colors
        self.update_image(self.image)

