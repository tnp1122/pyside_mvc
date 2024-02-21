from PySide6.QtWidgets import QWidget, QTabWidget

from ui.common import BaseTabWidgetView
from ui.tabs.experiment.window.snapshot.capture import PlateCaptureController


class PlateSnapshotView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setTabPosition(QTabWidget.South)

        self.plate_capture = PlateCaptureController()
        self.color_extract = QWidget()
        self.color_graph = QWidget()
        self.color_difference = QWidget()

        self.addTab(self.plate_capture.view, "플레이트 캡처")
        self.addTab(self.color_extract, "색 추출")
        self.addTab(self.color_graph, "그래프")
        self.addTab(self.color_difference, "색 차이")
