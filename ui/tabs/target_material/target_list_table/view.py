from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QSizePolicy, QHBoxLayout, QWidget

from ui.common import BaseTableWidgetView, CurvedCornerButton


class TargetListTableView(BaseTableWidgetView):
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

    def set_table_items(self, target_list):
        self.clear_table()

        for row, target in enumerate(target_list):
            self.insertRow(row)
            target_name = QTableWidgetItem(target["name"])

            self.setItem(row, 0, target_name)

            cell = self.item(row, 0)
            if cell:
                self.set_editable(cell, False)

        count = self.rowCount()
        self.insertRow(count)
        btn = CurvedCornerButton("추가")
        btn.clicked.connect(self.add_new_row)
        self._adjust_button_size(btn)

        lyt_btn = QHBoxLayout()
        lyt_btn.addWidget(btn)
        lyt_btn.setContentsMargins(0, 0, 0, 0)
        lyt_btn.setSpacing(5)
        container = QWidget()
        container.setLayout(lyt_btn)

        self.setCellWidget(count, 0, container)

        self.resizeRowsToContents()
        self.resizeColumnToContents(1)

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
