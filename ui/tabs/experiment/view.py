from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QSplitter

from ui.common import BaseWidgetView
from ui.tabs.experiment.explorer import ExplorerController
from ui.tabs.experiment.window import ExperimentWindowController


class ExperimentView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Horizontal)

        self.explorer = ExplorerController()
        self.window_widget = ExperimentWindowController()

        self.splitter.addWidget(self.explorer.view)
        self.splitter.addWidget(self.window_widget.view)
        lyt.addWidget(self.splitter)
        self.splitter.setSizes([1, 1000])
