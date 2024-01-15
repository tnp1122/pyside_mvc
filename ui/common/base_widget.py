from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QStackedWidget, QTabWidget, QTableWidget


class BaseViewMixin:
    ui_initialized_signal = Signal()

    def emit_ui_initialized_signal(self):
        self.ui_initialized_signal.emit()


class BaseViewMixinV2:
    def init_view(self):
        # print(f"parent init view")
        pass


class BaseWidgetViewV2(BaseViewMixinV2, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class BaseWidgetView(BaseViewMixin, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class BaseStackedWidgetView(BaseViewMixin, QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class BaseTabWidgetView(BaseViewMixin, QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class BaseTableWidgetView(BaseViewMixin, QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
