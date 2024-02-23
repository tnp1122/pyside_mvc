from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel

from ui.common import BaseWidgetView
from ui.tabs.experiment.window.snapshot.capture.capture_list import CaptureListController


class PlateCaptureView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def closeEvent(self, event):
        self.capture_list.close()

        super().closeEvent(event)

    def init_view(self):
        super().init_view()

        lyt_top = QHBoxLayout()

        lyt_capture_window = QVBoxLayout()

        image_view = QLabel("이미지")
        self.capture_list = CaptureListController()
        self.capture_list.set_unit_size(300, 500)
        lyt_content = QHBoxLayout()
        lyt_content.addWidget(image_view)
        lyt_content.addWidget(self.capture_list.view)

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_top)
        lyt.addLayout(lyt_content)
