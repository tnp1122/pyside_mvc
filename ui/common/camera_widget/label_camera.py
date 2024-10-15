import logging
import math

import numpy as np
from PySide6.QtCore import Signal, QRect, Qt
from PySide6.QtGui import QPixmap, QFont, QPainter, QPen, QMouseEvent
from PySide6.QtWidgets import QLabel, QSizePolicy

from models import Image
from models.snapshot import Snapshot
from ui.common.camera_widget.camera_widget_status import CameraWidgetStatus
from util import image_converter as ic
from util.camera_manager import CameraUnit, toupcam
from util.enums import LabCorrectionType


class LabelCamera(QLabel):
    camera_unit = CameraUnit()
    snapshot_initialized_signal = Signal()

    def __init__(self, status: CameraWidgetStatus):
        super().__init__("No Image")

        self.status = status

        self.initialized = False
        self.snapshot_initialized = False

        self.image = None
        self.sensor_indexes = []
        self.sensor_colors = []
        self.wb_x, self.wb_y, self.wb_width, self.wb_height = None, None, None, None

        self.setStyleSheet("border: 1px solid black")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.camera_unit.evtCallback.connect(self.on_event_callback)
        self.camera_unit.signal_image.connect(self.update_image)

    def calculate_sensor_positions(self):
        sensor_positions = []
        snapshot = self.status.snapshot_instance
        x, y, _, _ = snapshot.plate_position.get_crop_area()
        row_axes, column_axes = snapshot.plate_position.rows, snapshot.plate_position.columns

        for idx in range(96):
            solvent_idx, additive_idx = divmod(idx, 8)
            if snapshot.plate_position.direction == 0:
                sensor_x = x + column_axes[solvent_idx]
                sensor_y = y + row_axes[additive_idx]
            else:
                sensor_x = x + column_axes[additive_idx]
                sensor_y = y + row_axes[abs(solvent_idx - 11)]
            sensor_positions.append((sensor_x, sensor_y))
        return sensor_positions

    def is_within_circle(self, clicked_x, clicked_y, sensor_x, sensor_y, r=5):
        return math.sqrt(
            (clicked_x - sensor_x) ** 2 + (clicked_y - sensor_y) ** 2) <= self.status.snapshot_instance.mask.radius + r

    def mouseReleaseEvent(self, event: QMouseEvent):
        scaled_pixmap_size = self.pixmap().size()
        scale_x = self.image.shape[1] / scaled_pixmap_size.width()
        scale_y = self.image.shape[0] / scaled_pixmap_size.height()
        clicked_x = event.position().x() * scale_x
        clicked_y = event.position().y() * scale_y

        sensor_positions = self.calculate_sensor_positions()
        for idx, (sensor_x, sensor_y) in enumerate(sensor_positions):
            if self.is_within_circle(clicked_x, clicked_y, sensor_x, sensor_y):
                self.status.set_lab_correction_reference_hole_index(idx)
                break
        super().mousePressEvent(event)

    def on_event_callback(self, nEvent):
        if self.camera_unit.cam:
            if nEvent == toupcam.TOUPCAM_EVENT_ERROR:
                self.camera_unit.close_camera()
                logging.error("Generic Error.: 카메라 상태를 확인하세요.")

    def adjust_size(self):
        pixmap = self.pixmap()
        if not pixmap:
            return

        img_width = pixmap.width()
        img_height = pixmap.height()
        height = self.height()

        new_width = int(height * img_width / img_height)
        self.setFixedWidth(new_width)

        return self.width()

    def update_image(self, image: np.ndarray = None):
        if image is not None:
            self.image = image
            pixmap = ic.array_to_q_pixmap(image, True)

            self.paint_wb_roi(pixmap)
            self.paint_plate_border(pixmap)
            self.paint_whole_halls(pixmap)

            self.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio))

            if not self.initialized:
                self.adjust_size()
                self.initialized = True

            if not self.snapshot_initialized:
                snapshot: Snapshot = self.status.snapshot_instance
                snapshot.init_origin_image(Image(image))
                snapshot.mask.set_flare_threshold(255)
                self.snapshot_initialized = True
                self.snapshot_initialized_signal.emit()

    def refresh_paint(self):
        self.update_image(self.image)

    def paint_wb_roi(self, pixmap: QPixmap):
        if self.wb_x is None or not self.status.wb_roi_visible or not self.status.setting_visible:
            return

        rect = QRect(self.wb_x, self.wb_y, self.wb_width, self.wb_height)
        text = "화이트 밸런스"
        text_rect = QRect(self.wb_x, self.wb_y - 40, 200, 40)
        font = QFont("Malgun Gothic", 22, QFont.Bold)
        # font.setBold(True)

        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 5))
        painter.setFont(font)

        painter.drawRect(rect)
        painter.drawText(text_rect, Qt.AlignLeft, text)
        painter.end()

    def paint_plate_border(self, pixmap: QPixmap):
        if self.status.plate_border_visible and not self.status.lab_roi_visible:
            snapshot = self.status.snapshot_instance
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.red, 5))
            self.draw_plate(painter, snapshot)
            painter.end()

    def paint_whole_halls(self, pixmap: QPixmap):
        if self.status.lab_roi_visible:
            snapshot = self.status.snapshot_instance
            painter = QPainter(pixmap)
            self.draw_plate(painter, snapshot, highlight=True)
            painter.end()

    def draw_plate(self, painter, snapshot, highlight=False):
        x, y, width, height = snapshot.plate_position.get_crop_area()
        painter.setPen(QPen(Qt.gray, 5))
        painter.drawRect(x, y, width, height)
        for idx in range(96):
            if highlight and idx == self.status.lab_correction_reference_hole_index and self.status.lab_correction_type == LabCorrectionType.SINGLE_HALL_ROI:
                pen_color = Qt.green
            else:
                pen_color = Qt.gray
            # pen_color = Qt.green if highlight and idx == self.status.lab_standard_hole_index else Qt.gray
            painter.setPen(QPen(pen_color, 5))
            solvent_idx, additive_idx = divmod(idx, 8)
            sensor_x, sensor_y = self.get_sensor_position(snapshot, solvent_idx, additive_idx)
            painter.drawEllipse(sensor_x - snapshot.mask.radius, sensor_y - snapshot.mask.radius,
                                snapshot.mask.radius * 2, snapshot.mask.radius * 2)

    def get_sensor_position(self, snapshot, solvent_idx, additive_idx):
        x, y = snapshot.plate_position.get_crop_area()[:2]
        row_axes, column_axes = snapshot.plate_position.rows, snapshot.plate_position.columns
        if snapshot.plate_position.direction == 0:
            return x + column_axes[solvent_idx], y + row_axes[additive_idx]
        return x + column_axes[additive_idx], y + row_axes[abs(solvent_idx - 11)]

    def update_wb_roi(self, x, y, width, height):
        self.wb_x, self.wb_y, self.wb_width, self.wb_height = x, y, width, height
        self.refresh_paint()

    def take_snapshot(self) -> Snapshot:
        if self.image is not None:
            snapshot: Snapshot = self.status.snapshot_instance
            snapshot.change_origin_image(Image(self.image))
            return snapshot

    def set_sensor_indexes(self, indexes: list, colors: list):
        self.sensor_indexes = indexes
        self.sensor_colors = colors
        self.refresh_paint()
