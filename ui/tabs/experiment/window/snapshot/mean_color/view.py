from PySide6.QtWidgets import QVBoxLayout

from ui.common import BaseWidgetView, MileStoneRadio
from ui.tabs.experiment.window.snapshot.mean_color.image_list import ImageListController


class MeanColorView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.radio = MileStoneRadio(["평균 색", "실제 색"])
        self.image_list = ImageListController()

        lyt = QVBoxLayout(self)
        lyt.addWidget(self.radio)
        lyt.addStretch()
        lyt.addWidget(self.image_list.view)
        lyt.addStretch()
