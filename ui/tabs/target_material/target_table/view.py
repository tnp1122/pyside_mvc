from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHeaderView

from ui.common import BaseTableWidgetView


class TargetTableView(BaseTableWidgetView):
    add_signal = Signal(int)
    confirm_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setMinimumWidth(200)
        self.setColumnCount(1)

        headers = ["타겟 물질"]
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
