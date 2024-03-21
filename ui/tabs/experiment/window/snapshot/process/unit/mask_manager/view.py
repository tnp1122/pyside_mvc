from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFrame, QLabel

from model import Image
from ui.common import MileStoneRadio, BaseDialogView, ColoredButton
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import Masking
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics.controller import MaskGraphicsController


class MaskManagerView(BaseDialogView):
    width_pos_text = 50
    width_radius_text = 35

    def __init__(self, parent=None, origin_image: Image = None):
        self.origin_image = origin_image
        super().__init__(parent)

    def closeEvent(self, event):
        self.graphics.close()
        self.masking.close()

        super().closeEvent(event)

    def init_view(self):
        self.setWindowTitle("마스크 영역 지정")

        self.view_radio = MileStoneRadio(["원본", "마스킹 구역 지정", "마스킹 영역 보기"])
        self.btn_apply = ColoredButton("적용", background_color="red")

        lyt_btn = QHBoxLayout()
        lyt_btn.addWidget(self.view_radio)
        lyt_btn.addWidget(self.btn_apply)

        self.graphics = MaskGraphicsController()
        self.graphics.set_scene(self.origin_image)
        self.graphics.border_changed.connect(self.update_border_position_text)

        self.lyt_bottom_district = self.init_bottom_district()
        self.lyt_bottom_masking = self.init_bottom_masking()
        self.set_bottom_lyt(0)

        self.lyt = QVBoxLayout(self)
        self.lyt.addLayout(lyt_btn)
        self.lyt.addWidget(self.graphics.view)
        self.lyt.addLayout(self.lyt_bottom_district)
        self.lyt.addLayout(self.lyt_bottom_masking)

        self.init_text()

    def init_text(self):
        self.update_border_position_text()
        self.ET_r.setText(str(self.graphics.model.circle_radius))

        self.ET_threshold.setText(str(self.masking.threshold))

    def update_border_position_text(self):
        model = self.graphics.model

        self.ET_x.setText(str(int(model.area_x)))
        self.ET_y.setText(str(int(model.area_y)))
        self.ET_w.setText(str(int(model.area_width)))
        self.ET_h.setText(str(int(model.area_height)))

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

        self.ET_x.setFixedWidth(self.width_pos_text)
        self.ET_y.setFixedWidth(self.width_pos_text)
        self.ET_w.setFixedWidth(self.width_pos_text)
        self.ET_h.setFixedWidth(self.width_pos_text)
        self.ET_r.setFixedWidth(self.width_radius_text)

        style = "border: 0px;"
        self.ET_x.setStyleSheet(style)
        self.ET_y.setStyleSheet(style)
        self.ET_w.setStyleSheet(style)
        self.ET_h.setStyleSheet(style)
        self.ET_x.setReadOnly(True)
        self.ET_y.setReadOnly(True)
        self.ET_w.setReadOnly(True)
        self.ET_h.setReadOnly(True)

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

    def init_bottom_masking(self):
        self.masking = Masking(self.origin_image.array)
        self.set_circle_mask()  # 마스크 set을 해둬야 캡쳐 유닛에서 픽스맵 가져올 수 있음

        lyt = QHBoxLayout()
        self.btn_show_masking = QPushButton("마스킹 영역 수정")
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)

        lb_threshold = QLabel("threshold")
        self.ET_threshold = QLineEdit()
        validator = QIntValidator(1, 255)
        self.ET_threshold.setValidator(validator)
        self.ET_threshold.setFixedWidth(40)

        lyt.addWidget(self.btn_show_masking)
        lyt.addWidget(divider)
        lyt.addWidget(lb_threshold)
        lyt.addWidget(self.ET_threshold)
        lyt.addStretch()

        return lyt

    def set_circle_mask(self):
        circle_mask_info = self.graphics.get_circle_mask_info()
        self.masking.set_circle_mask(circle_mask_info)
