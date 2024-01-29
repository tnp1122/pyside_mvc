from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QSplitter, QPushButton, QSizePolicy

from ui.common import BaseWidgetView
from ui.tabs.experiment.explorer import ExplorerController


class ExperimentView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        lyt = QVBoxLayout(self)

        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Horizontal)

        self.explorer = ExplorerController()
        btn = QPushButton("위젯")
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.splitter.addWidget(self.explorer.view)
        self.splitter.addWidget(btn)

        lyt.addWidget(self.splitter)
