from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy

from ui.common import BaseWidgetView, ImageButton, Logo, ColoredButton, RefreshButton, Toggle
from ui.common.tree_view import TreeView

from util import local_storage_manager as lsm


class ExplorerView(BaseWidgetView):
    resize_event = Signal(QResizeEvent)

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(10, 10, 0, 0)

        lyt_top = QHBoxLayout()
        self.btn_add = ColoredButton("실험 추가", size=(65, 30))
        self.btn_refresh = RefreshButton()
        expand_img = lsm.get_static_image_path("expand_arrow.png")
        self.btn_toggle = Toggle("연속촬영", "스냅샷", (90, 26))
        self.btn_expand = ImageButton(image=expand_img, size=(30, 30))
        lyt_top.addWidget(self.btn_add)
        lyt_top.addWidget(self.btn_refresh)
        lyt_top.addStretch()
        lyt_top.addWidget(self.btn_toggle)

        self.tree = TreeView()

        self.btn_toggle.switched.connect(self.tree.switch_visibility)

        logo = Logo(size=(200, 200))

        lyt.addLayout(lyt_top)
        lyt.addWidget(self.tree)
        lyt.addWidget(logo, alignment=Qt.AlignHCenter)

    def set_tree_items(self, experiment_tree):
        self.tree.set_tree(experiment_tree)
