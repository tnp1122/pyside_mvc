import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy

from ui.common import BaseWidgetView, ImageButton, Logo, ColoredButton, RefreshButton
from ui.common.tree_view import TreeView


class ExplorerView(BaseWidgetView):
    resize_event = Signal(QResizeEvent)

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lyt = QVBoxLayout(self)

        lyt_top = QHBoxLayout()
        self.btn_add = ColoredButton("실험 추가")
        self.btn_refresh = RefreshButton()
        expand_img = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  "../../../../static/image/expand_arrow.png")
        self.btn_toggle = ImageButton(image=expand_img, size=(30, 30), degree=90)
        lyt_top.addWidget(self.btn_add)
        lyt_top.addWidget(self.btn_refresh)
        lyt_top.addStretch()
        lyt_top.addWidget(self.btn_toggle)

        self.tree = TreeView()

        logo = Logo(size=(200, 200))

        lyt.addLayout(lyt_top)
        lyt.addWidget(self.tree)
        lyt.addWidget(logo, alignment=Qt.AlignHCenter)

    def set_tree_items(self, experiment_tree):
        self.tree.set_tree(experiment_tree)
