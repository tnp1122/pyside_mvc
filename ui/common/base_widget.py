from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class BaseWidgetView(QWidget):
    ui_initialized_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def emit_ui_initialized_signal(self):
        self.ui_initialized_signal.emit()
