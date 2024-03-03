from PySide6.QtWidgets import QVBoxLayout

from ui.common import BaseWidgetView, MileStoneRadio
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListController
from ui.tabs.experiment.window.snapshot.process.unit import PlateCaptureUnitController, PlateCaptureUnitView
from ui.tabs.experiment.window.snapshot.extract.image_list import ImageListController


class ColorExtractView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.radio = MileStoneRadio(["색 추출", "실제 색"])
        self.image_list = ImageListController()
        self.image_list.set_image_size(300, 500)

        lyt = QVBoxLayout(self)
        lyt.addWidget(self.radio)
        lyt.addStretch()
        lyt.addWidget(self.image_list.view)
        lyt.addStretch()

