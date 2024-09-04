import logging

import numpy as np
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy

from util import image_converter as ic
from util.camera_manager import CameraUnit, toupcam


class CameraViewer(QWidget):
    camera_unit = CameraUnit()

    def __init__(self, parent=None, setting_visible=True):
        super().__init__(parent)
        self.setting_visible = setting_visible
        self.lb_initialized = False

        self.image = None
        self.wb_x, self.wb_y, self.wb_width, self.wb_height = None, None, None, None

        self.btn_switch_setting_visible = QPushButton("카메라 설정 열기")
        self.btn_set_mask_area = QPushButton("마스크 설정 열기")
        self.btn_init_mask_area = QPushButton("마스크 영역 초기화")
        self.btn_hide_mask_area = QPushButton("마스크 영역 숨기기")
        self.btn_set_mask_area.setEnabled(False)
        self.btn_init_mask_area.setEnabled(False)
        self.btn_hide_mask_area.setEnabled(False)
        lyt_btn1 = QHBoxLayout()
        lyt_btn2 = QHBoxLayout()
        lyt_btn1.addWidget(self.btn_switch_setting_visible)
        lyt_btn1.addWidget(self.btn_set_mask_area)
        lyt_btn2.addWidget(self.btn_init_mask_area)
        lyt_btn2.addWidget(self.btn_hide_mask_area)
        lyt_btn = QVBoxLayout()
        lyt_btn.addLayout(lyt_btn1)
        lyt_btn.addLayout(lyt_btn2)

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_label_size()

    def update_image(self, image: np.ndarray):
        if image is not None:
            self.image = image
            pixmap = ic.array_to_q_pixmap(image, True)

            self.paint_wb_roi(pixmap)
            self.lb_image.setPixmap(pixmap.scaled(self.lb_image.size(), Qt.KeepAspectRatio))
            if not self.lb_initialized:
                self.adjust_label_size()
                self.lb_initialized = True

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
        if self.wb_x is None:
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

    """ 이벤트 핸들러 """

    def on_event_callback(self, nEvent):
        if self.camera_unit.cam:
            if nEvent == toupcam.TOUPCAM_EVENT_ERROR:
                self.camera_unit.close_camera()
                logging.error("Generic Error.: 카메라 상태를 확인하세요.")

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
