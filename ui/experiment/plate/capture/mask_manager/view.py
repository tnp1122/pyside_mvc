from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget

from ui import BaseWidgetView, MileStone
from ui.experiment.plate.capture.mask_manager.mask_district.controller.mask_district_widget import MaskDistrictWidget


class MaskManagerView(BaseWidgetView):
    def __init__(self, origin_image, parent=None):
        super().__init__(parent)

        self.init_ui(origin_image)

    def init_ui(self, origin_image):
        self.setWindowTitle("마스크 영역 지정")
        lyt = QVBoxLayout(self)

        lyt_mile_stone = QHBoxLayout()
        lyt.addLayout(lyt_mile_stone)
        self.btn_mask_district = MileStone("마스킹 구역 지정")
        self.btn_mask_area = MileStone("마스킹 영역 보기")
        lyt_mile_stone.addWidget(self.btn_mask_district)
        lyt_mile_stone.addWidget(self.btn_mask_area)

        district_widget = MaskDistrictWidget(origin_image)
        stack = QStackedWidget()
        stack.addWidget(district_widget.view)
        lyt.addWidget(stack)

        self.emit_ui_initialized_signal()
