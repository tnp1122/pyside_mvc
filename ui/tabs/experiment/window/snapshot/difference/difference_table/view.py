from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

from ui.common import BaseTableWidgetView


class ColorDifferenceTableView(BaseTableWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

    def set_table_items(self, items):
        self.clear_table()

        for row, row_datas in enumerate(items):
            row_count = self.rowCount()
            self.insertRow(row_count)
            for column, data in enumerate(row_datas):
                item = QTableWidgetItem("{:.3f}".format(data))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, column, item)
