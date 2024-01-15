from PySide6.QtWidgets import QWidget, QStackedWidget, QTabWidget, QTableWidget, QGraphicsView


class BaseViewMixin:
    def init_view(self):
        # print(f"parent init view")
        pass

    def on_view_initialized(self):
        # print(f"on view initiailized")
        pass


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


class BaseGraphicsView(BaseViewMixin, QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
