from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QStackedWidget, QTabWidget, QTableWidget, QGraphicsView, QTreeView, QSplitter, \
    QScrollArea, QVBoxLayout, QSizePolicy, QTableWidgetItem, QPushButton, QDialog


def close_event_deco(cls):
    def wrapper(func):
        def closeEvent(self, event):
            self.closing.emit()
            self.deleteLater()
            func(self, event)

        return closeEvent

    cls.closeEvent = wrapper(cls.closeEvent)
    return cls


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


@close_event_deco
class BaseWidgetView(BaseViewMixin, QWidget):
    closing = Signal()

    def __init__(self, parent=None, args=None):
        QWidget.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


@close_event_deco
class BaseDialogView(BaseViewMixin, QDialog):
    closing = Signal()

    def __init__(self, parent=None, args=None):
        QDialog.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


@close_event_deco
class BaseStackedWidgetView(BaseViewMixin, QStackedWidget):
    closing = Signal()

    def __init__(self, parent=None, args=None):
        QStackedWidget.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


@close_event_deco
class BaseTabWidgetView(BaseViewMixin, QTabWidget):
    closing = Signal()

    def __init__(self, parent=None, args=None):
        QTabWidget.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


@close_event_deco
class BaseGraphicsView(BaseViewMixin, QGraphicsView):
    closing = Signal()

    def __init__(self, parent=None, args=None):
        QGraphicsView.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


@close_event_deco
class BaseTreeView(BaseViewMixin, QTreeView):
    closing = Signal()

    def __init__(self, parent=None, args=None):
        QTreeView.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


@close_event_deco
class BaseSplitterView(BaseViewMixin, QSplitter):
    closing = Signal()

    def __init__(self, parent=None, args=None):
        QSplitter.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


@close_event_deco
class BaseScrollAreaView(BaseViewMixin, QScrollArea):
    closing = Signal()

    def __init__(self, parent=None, args=None):
        QScrollArea.__init__(self, parent)
        BaseViewMixin.__init__(self, args)


@close_event_deco
class BaseTableWidgetView(BaseViewMixin, QTableWidget):
    closing = Signal()

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

        self.set_add_button()

    def set_add_button(self):
        count = self.rowCount()
        self.insertRow(count)
        self.setSpan(count, 0, 1, self.horizontalHeader().length())

        btn = QPushButton("추가")
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
