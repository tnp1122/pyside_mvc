from PySide6.QtGui import QImage, QIntValidator, QDoubleValidator
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFrame, QLabel

from ui import BaseWidgetView, MileStoneRadio
from ui.experiment.plate.capture.mask_manager import Masking
from ui.experiment.plate.capture.mask_manager.mask_graphics.controller.main import MaskGraphicsWidget


class MaskManagerView(BaseWidgetView):
    def __init__(self, origin_image, parent=None):
        super().__init__(parent)

        self._origin_image = origin_image

    @property
    def origin_image(self):
        return self._origin_image

    def init_ui(self):
        self.setWindowTitle("마스크 영역 지정")
        lyt = QVBoxLayout(self)

        self.view_radio = MileStoneRadio(["원본", "마스킹 구역 지정", "마스킹 영역 보기"])
        lyt.addWidget(self.view_radio)

        self.graphics = MaskGraphicsWidget(QImage(self.origin_image))
        lyt.addWidget(self.graphics.view)

        self.lyt_bottom_district = self.init_bottom_district() #QHBoxLayout()
        lyt.addLayout(self.lyt_bottom_district)

        self.masking = Masking(self.origin_image)
        self.lyt_bottom_masking = QHBoxLayout()
        lyt.addLayout(self.lyt_bottom_masking)
        self.btn_show_masking = QPushButton("마스킹 영역 수정")
        self.lyt_bottom_masking.addWidget(self.btn_show_masking)
        self.lyt_bottom_masking.addStretch()
        lyt.addLayout(self.lyt_bottom_masking)

        self.set_bottom_lyt(0)
        self.emit_ui_initialized_signal()

    def set_bottom_lyt(self, index):
        if index == 0:
            self.set_bottom_lyt_visible(1, False)
            self.set_bottom_lyt_visible(2, False)
        elif index == 1:
            self.set_bottom_lyt_visible(1, True)
            self.set_bottom_lyt_visible(2, False)
        else:
            self.set_bottom_lyt_visible(1, False)
            self.set_bottom_lyt_visible(2, True)

    def set_bottom_lyt_visible(self, index, visible):
        if index == 1:
            lyt = self.lyt_bottom_district
        else:
            lyt = self.lyt_bottom_masking

        for idx in range(lyt.count() - 1):
            widget = lyt.itemAt(idx).widget()
            widget.setVisible(visible)

    def init_bottom_district(self):
        lyt = QHBoxLayout()
        self.btn_set_horizontal = QPushButton("가로")
        self.btn_set_vertical = QPushButton("세로")
        self.btn_circle = QPushButton("원 보기")
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)

        lb_x = QLabel("x")
        lb_y = QLabel("y")
        lb_w = QLabel("width")
        lb_h = QLabel("height")
        lb_r = QLabel("반지름")
        validator = QDoubleValidator(0.0, 9999.99, 3)
        validator_int = QIntValidator(1, 999)
        validator.setNotation(QDoubleValidator.StandardNotation)

        self.ET_x = QLineEdit()
        self.ET_y = QLineEdit()
        self.ET_w = QLineEdit()
        self.ET_h = QLineEdit()
        self.ET_r = QLineEdit()

        self.ET_x.setValidator(validator)
        self.ET_y.setValidator(validator)
        self.ET_w.setValidator(validator)
        self.ET_h.setValidator(validator)
        self.ET_r.setValidator(validator_int)

        self.ET_x.setFixedWidth(70)
        self.ET_y.setFixedWidth(70)
        self.ET_w.setFixedWidth(70)
        self.ET_h.setFixedWidth(70)
        self.ET_r.setFixedWidth(40)

        lyt.addWidget(self.btn_set_horizontal)
        lyt.addWidget(self.btn_set_vertical)
        lyt.addWidget(self.btn_circle)
        lyt.addWidget(divider)
        lyt.addWidget(lb_x)
        lyt.addWidget(self.ET_x)
        lyt.addWidget(lb_y)
        lyt.addWidget(self.ET_y)
        lyt.addWidget(lb_w)
        lyt.addWidget(self.ET_w)
        lyt.addWidget(lb_h)
        lyt.addWidget(self.ET_h)
        lyt.addWidget(lb_r)
        lyt.addWidget(self.ET_r)
        lyt.addStretch()

        return lyt
