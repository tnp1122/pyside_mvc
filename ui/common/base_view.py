from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QStackedWidget, QTabWidget, QTableWidget, QGraphicsView, QTreeView, QSplitter, \
    QScrollArea, QVBoxLayout, QSizePolicy, QTableWidgetItem, QHBoxLayout


class LateInit(QObject):
    signal = Signal()

    def __init__(self):
        super().__init__()


class BaseViewMixin:
    def __init__(self, args=None):
        self._late_init = LateInit()

    def init_view(self):
        # print(f"parent init view")
        pass

    def on_view_initialized(self):
        # print(f"on view initiailized")
        pass

    def late_init(self):
        self._late_init.signal.emit()

    def with_container(self, widget, mode=0):
        container = QWidget()
        lyt = QVBoxLayout(container)
        if mode == 0:
            lyt.addWidget(widget, stretch=1, alignment=Qt.AlignHCenter)
        else:
            lyt.addWidget(widget)
        lyt.setContentsMargins(0, 0, 0, 0)

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


class BaseTableWidgetView(BaseViewMixin, QTableWidget):

    def __init__(self, parent=None, args=None):
        QTableWidget.__init__(self, parent)
        BaseViewMixin.__init__(self, args)
        self.cellClicked.connect(self.on_cell_clicked)

    def set_table_items(self, items):
        self.clear_table()

        for row, item in enumerate(items):
            self.insertRow(row)
            cell = QTableWidgetItem(item["name"])

            self.setItem(row, 0, cell)
            self.set_editable(cell, False)

        count = self.rowCount()
        self.insertRow(count)
        btn = CurvedCornerButton("추가")
        btn.clicked.connect(self.add_new_row)
        self._adjust_button_size(btn)

        container = self.with_container(btn, mode=1)

        self.setCellWidget(count, 0, container)

    def on_cell_clicked(self, row, column):
        self.editItem(self.item(row, column))

    def clear_table(self):
        self.clearContents()
        self.setRowCount(0)

    def _adjust_button_size(self, button):
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setStyleSheet("QPushButton { text-align: center; padding: 5px; }")

    def set_editable(self, cell, editable=True):
        flags = cell.flags()
        if editable:
            flags |= Qt.ItemIsEditable
        else:
            flags &= ~Qt.ItemIsEditable
        cell.setFlags(flags)

    def add_new_row(self):
        count = self.rowCount()
        font = QFont()
        font.setBold(True)
        item = QTableWidgetItem("")
        item.setFont(font)
        self.insertRow(count)
        self.setItem(count, 0, item)
