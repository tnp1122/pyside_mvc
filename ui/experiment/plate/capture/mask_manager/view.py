from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton

from ui import BaseWidgetView, MileStoneRadio
from ui.experiment.plate.capture.mask_manager.mask_district.controller.mask_district_widget import MaskDistrictWidget


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

        self.graphics = MaskDistrictWidget(self.origin_image)
        lyt.addWidget(self.graphics.view)

        lyt_district_button = QHBoxLayout()
        lyt.addLayout(lyt_district_button)
        self.btn_set_horizontal = QPushButton("가로")
        self.btn_set_vertical = QPushButton("세로")
        self.btn_circle = QPushButton("원 보기")
        lyt_district_button.addWidget(self.btn_set_horizontal)
        lyt_district_button.addWidget(self.btn_set_vertical)
        lyt_district_button.addWidget(self.btn_circle)
        lyt_district_button.addStretch()
        lyt.addLayout(lyt_district_button)

        self.emit_ui_initialized_signal()
