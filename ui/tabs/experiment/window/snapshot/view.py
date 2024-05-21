from PySide6.QtWidgets import QWidget, QTabWidget

from ui.common import BaseTabWidgetView
from ui.tabs.experiment.window.snapshot.difference import ColorDifferenceController
from ui.tabs.experiment.window.snapshot.process import SnapshotProcessController
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListView
from ui.tabs.experiment.window.snapshot.mean_color import MeanColorController
from util.colors import WHITE_GRAY


class PlateSnapshotView(BaseTabWidgetView):
    def __init__(self, parent=None, snapshot_info=None):
        self.snapshot_info = snapshot_info

        super().__init__(parent)

    def closeEvent(self, event):
        self.plate_process.close()
        self.mean_color.close()
        self.color_graph.close()
        self.color_difference.close()
        super().closeEvent(event)

    def init_view(self):
        super().init_view()

        self.setTabPosition(QTabWidget.South)

        self.plate_process = SnapshotProcessController(snapshot_info=self.snapshot_info)
        self.mean_color = MeanColorController()
        self.color_graph = QWidget()
        self.color_difference = ColorDifferenceController(snapshot_info=self.snapshot_info)

        self.addTab(self.plate_process.view, "이미지 처리")
        self.addTab(self.mean_color.view, "평균 색")
        self.addTab(self.color_graph, "그래프")
        self.addTab(self.color_difference.view, "색 차이")

    def set_style_sheet(self):
        self.setObjectName("PlateSnapshotBar")
        self.tabBar().setObjectName("PlateSnapshotBarTap")
        style = f"""
            #PlateSnapshotBar::pane {{
                background-color: {WHITE_GRAY};
                border: none;
        }}
            #PlateSnapshotBarTap::tab {{
                margin: 0px;
                padding: 5px 10px 5px 10px;
                background-color: white;
                border: 0.5px solid lightgray;
                border-top: none;
        }}
            #PlateSnapshotBatTap::tab:first {{
                border-left: none;
        }}
            #PlateSnapshotBarTap::tab:selected {{
                background-color: {WHITE_GRAY};
                border-color: {WHITE_GRAY};
        }}
        """

        self.setStyleSheet(style)

    def set_targets(self, targets):
        capture_list_view: CaptureListView = self.plate_process.view.capture_list.view
        capture_list_view.set_targets(targets)
