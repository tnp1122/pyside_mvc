from PySide6.QtWidgets import QWidget, QTabWidget

from ui.common import BaseTabWidgetView
from ui.tabs.experiment.window.snapshot.capture import PlateCaptureController
from ui.tabs.experiment.window.snapshot.capture.capture_list import CaptureListView
from ui.tabs.experiment.window.snapshot.extract import ColorExtractController


class PlateSnapshotView(BaseTabWidgetView):
    def __init__(self, parent=None, plate_info=None):
        self.plate_info = plate_info

        super().__init__(parent)

    def closeEvent(self, event):
        self.plate_capture.close()
        self.color_extract.close()
        self.color_graph.close()
        self.color_difference.close()
        super().closeEvent(event)

    def init_view(self):
        super().init_view()

        self.setTabPosition(QTabWidget.South)

        self.plate_capture = PlateCaptureController(plate_info=self.plate_info)
        self.color_extract = ColorExtractController()
        self.color_graph = QWidget()
        self.color_difference = QWidget()

        self.addTab(self.plate_capture.view, "플레이트 캡처")
        self.addTab(self.color_extract.view, "색 추출")
        self.addTab(self.color_graph, "그래프")
        self.addTab(self.color_difference, "색 차이")

    def set_targets(self, targets):
        capture_list_view: CaptureListView = self.plate_capture.view.capture_list.view
        capture_list_view.set_targets(targets)
