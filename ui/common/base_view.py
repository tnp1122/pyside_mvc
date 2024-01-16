from PySide6.QtWidgets import QWidget, QStackedWidget, QTabWidget, QTableWidget, QGraphicsView


class BaseViewMixin:
    def __init__(self, args=None):
        pass

    def init_view(self):
        # print(f"parent init view")
        pass

    def on_view_initialized(self):
        # print(f"on view initiailized")
        pass


class BaseWidgetView(BaseViewMixin, QWidget):
    def __init__(self, parent=None, args=None):
        QWidget.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


class BaseStackedWidgetView(BaseViewMixin, QStackedWidget):
    def __init__(self, parent=None, args=None):
        QStackedWidget.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


class BaseTabWidgetView(BaseViewMixin, QTabWidget):
    def __init__(self, parent=None, args=None):
        QTabWidget.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


class BaseTableWidgetView(BaseViewMixin, QTableWidget):
    def __init__(self, parent=None, args=None):
        QTableWidget.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


class BaseGraphicsView(BaseViewMixin, QGraphicsView):
    def __init__(self, parent=None, args=None):
        QGraphicsView.__init__(self, parent)
        BaseViewMixin.__init__(self, args)
