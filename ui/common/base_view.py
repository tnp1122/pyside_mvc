from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QStackedWidget, QTabWidget, QTableWidget, QGraphicsView, QTreeView, QSplitter, \
    QScrollArea, QVBoxLayout


class BaseViewMixin:
    def __init__(self, args=None):
        pass

    def init_view(self):
        # print(f"parent init view")
        pass

    def on_view_initialized(self):
        # print(f"on view initiailized")
        pass

    def with_container(self, widget):
        container = QWidget(self)
        lyt = QVBoxLayout(container)
        lyt.addWidget(widget, stretch=1, alignment=Qt.AlignHCenter)

        return container


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


class BaseTreeView(BaseViewMixin, QTreeView):
    def __init__(self, parent=None, args=None):
        QTreeView.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


class BaseSplitterView(BaseViewMixin, QSplitter):
    def __init__(self, parent=None, args=None):
        QSplitter.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


class BaseScrollAreaView(BaseViewMixin, QScrollArea):
    def __init__(self, parent=None, args=None):
        QScrollArea.__init__(self, parent)
        BaseViewMixin.__init__(self, args)
