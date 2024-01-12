from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from ui.common import BaseWidgetView
from ui.common.logo import Logo


class HomeView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        lyt = QVBoxLayout(self)

        lb_logo = Logo(with_title=True)

        lyt.addWidget(lb_logo, alignment=Qt.AlignVCenter | Qt.AlignHCenter)

        self.emit_ui_initialized_signal()