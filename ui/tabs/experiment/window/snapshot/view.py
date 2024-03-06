from PySide6.QtWidgets import QWidget, QTabWidget

from ui.common import BaseTabWidgetView
from ui.tabs.experiment.window.snapshot.difference import ColorDifferenceController
from ui.tabs.experiment.window.snapshot.process import PlateProcessController
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListView
from ui.tabs.experiment.window.snapshot.extract import ColorExtractController


class PlateSnapshotView(BaseTabWidgetView):
    def __init__(self, parent=None, snapshot_info=None):
        self.snapshot_info = snapshot_info

        super().__init__(parent)

    def closeEvent(self, event):
        self.plate_process.close()
        self.color_extract.close()
        self.color_graph.close()
        self.color_difference.close()
        super().closeEvent(event)

    def init_view(self):
        super().init_view()

        self.setTabPosition(QTabWidget.South)

        self.plate_process = PlateProcessController(snapshot_info=self.snapshot_info)
        self.color_extract = ColorExtractController()
        self.color_graph = QWidget()
        self.color_difference = ColorDifferenceController(snapshot_info=self.snapshot_info)

        self.addTab(self.plate_process.view, "이미지 처리")
        self.addTab(self.color_extract.view, "색 추출")
        self.addTab(self.color_graph, "그래프")
        self.addTab(self.color_difference.view, "색 차이")

    def set_targets(self, targets):
        capture_list_view: CaptureListView = self.plate_process.view.capture_list.view
        capture_list_view.set_targets(targets)
