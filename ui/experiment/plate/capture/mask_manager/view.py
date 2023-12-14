from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget, QPushButton

from ui import BaseWidgetView, MileStone
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

        lyt_mile_stone = QHBoxLayout()
        lyt.addLayout(lyt_mile_stone)
        self.btn_mask_district = MileStone("마스킹 구역 지정")
        self.btn_mask_area = MileStone("마스킹 영역 보기")
        lyt_mile_stone.addWidget(self.btn_mask_district)
        lyt_mile_stone.addWidget(self.btn_mask_area)

        stack = QStackedWidget()
        stack.addWidget(self.get_widget_district())
        lyt.addWidget(stack)

        self.emit_ui_initialized_signal()

    def get_widget_district(self):
        widget = QWidget()
        lyt = QHBoxLayout(widget)

        self.district_widget = MaskDistrictWidget(self.origin_image)
        lyt.addWidget(self.district_widget.view)

        lyt_buttons = QVBoxLayout()
        self.btn_set_horizontal = QPushButton("가로")
        self.btn_set_vertical = QPushButton("세로")
        lyt_buttons.addWidget(self.btn_set_horizontal)
        lyt_buttons.addWidget(self.btn_set_vertical)
        lyt.addLayout(lyt_buttons)

        return widget
