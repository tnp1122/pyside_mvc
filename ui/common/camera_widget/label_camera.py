import logging

import numpy as np
from PySide6.QtCore import Signal, QRect, Qt
from PySide6.QtGui import QPixmap, QFont, QPainter, QPen
from PySide6.QtWidgets import QLabel, QSizePolicy

from models import Image
from models.snapshot import Snapshot
from util import image_converter as ic
from util.camera_manager import CameraUnit, toupcam


class LabelCamera(QLabel):
    camera_unit = CameraUnit()
    snapshot_initialized_signal = Signal()

    def __init__(self, snapshot: Snapshot, wb_roi_visible=True, plate_border_visible=True):
        super().__init__("No Image")

        self.wb_roi_visible = wb_roi_visible
        self.plate_border_visible = plate_border_visible

        self.initialized = False
        self.snapshot_initialized = False

        self.image = None
        self.snapshot_instance = snapshot
        self.sensor_indexes = []
        self.sensor_colors = []
        self.wb_x, self.wb_y, self.wb_width, self.wb_height = None, None, None, None

        self.setStyleSheet("border: 1px solid black")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.camera_unit.evtCallback.connect(self.on_event_callback)
        self.camera_unit.signal_image.connect(self.update_image)

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

    def set_wb_roi_visible(self, visible):
        self.wb_roi_visible = visible
        self.update_image()

    def set_plate_border_visible(self, visible):
        self.plate_border_visible = visible
        self.update_image()

    def update_image(self, image: np.ndarray = None):
        if image is None:
            image = self.image

        if image is not None:
            self.image = image
            pixmap = ic.array_to_q_pixmap(image, True)

            self.paint_wb_roi(pixmap)
            self.paint_plate_border(pixmap)

            self.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio))

            if not self.initialized:
                self.adjust_size()
                self.initialized = True

            if not self.snapshot_initialized:
                snapshot: Snapshot = self.snapshot_instance
                snapshot.init_origin_image(Image(image))
                snapshot.mask.set_flare_threshold(255)
                self.snapshot_initialized = True
                self.snapshot_initialized_signal.emit()

    def paint_wb_roi(self, pixmap: QPixmap):
        if self.wb_x is None or not self.wb_roi_visible:
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
        if not self.plate_border_visible:
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

    def take_snapshot(self):
        if self.image is not None:
            snapshot: Snapshot = self.snapshot_instance
            snapshot.change_origin_image(Image(self.image))

    def set_sensor_indexes(self, indexes: list, colors: list):
        self.sensor_indexes = indexes
        self.sensor_colors = colors
        self.update_image(self.image)
