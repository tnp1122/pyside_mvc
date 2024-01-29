import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QSizePolicy

from ui.common import BaseWidgetView, ImageButton, Logo
from ui.common.tree_view import TreeView
from ui.tabs.experiment.explorer.explorer_tree import ExplorerTreeController


class ExplorerView(BaseWidgetView):
    resize_event = Signal(QResizeEvent)

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lyt = QVBoxLayout(self)

        lyt_toggle = QHBoxLayout()
        expand_img = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  "../../../../static/image/expand_left.png")
        self.btn_toggle = ImageButton(image=expand_img, size=(30, 30))
        lyt_toggle.addStretch()
        lyt_toggle.addWidget(self.btn_toggle)

        self.tree = TreeView()

        logo = Logo(size=(200, 200))

        lyt.addLayout(lyt_toggle)
        lyt.addWidget(self.tree)
        lyt.addWidget(logo, alignment=Qt.AlignHCenter)
