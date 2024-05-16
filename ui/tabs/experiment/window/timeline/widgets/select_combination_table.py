import json

from PySide6.QtCore import QSignalMapper, Qt, Signal
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout

from ui.common import BaseTableWidgetView, TableWidgetController


class SelectCombinationTableModel:
    def __init__(self):
        pass


class SelectCombinationTableView(BaseTableWidgetView):
    scroll_width = 17
    display_associations_changed = Signal(list)

    def __init__(self, parent=None):
        self.combination: dict = None

        super().__init__(parent)

        self.headers = ["순번", "용매", "첨가제", "그래프"]
        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.check_boxes = []
        self.display_association_indexes = []
        self.emit_signal_blocked = False

    def init_view(self):
        super().init_view()

        self.cb_display_all = QCheckBox()
        self.cb_display_all.stateChanged.connect(self.on_display_all_changed)

    def set_table_items(self, combination):
        self.combination = combination

        self.clear_table()
        self.set_first_row()

        self.mapper_change_display = QSignalMapper(self)
        self.mapper_change_display.mappedInt.connect(self.on_change_display)

        for row, association in enumerate(combination["sensor_associations"]):
            idx = association["idx"]
            sol_idx, add_idx = divmod(idx, 8)
            idx_str = f"{sol_idx + 1}-{chr(ord('A') + add_idx)}"

            sensor = association["sensor"]
            cb_display = QCheckBox()
            cb_display.stateChanged.connect(self.mapper_change_display.map)
            self.check_boxes.append(cb_display)
            self.mapper_change_display.setMapping(cb_display, row)
            widget_cb_display = QWidget()
            lyt_cb_display = QHBoxLayout(widget_cb_display)
            lyt_cb_display.addWidget(cb_display)
            lyt_cb_display.setAlignment(Qt.AlignCenter)
            lyt_cb_display.setContentsMargins(0, 0, 0, 0)

            cell_idx = QTableWidgetItem(idx_str)
            cell_solvent_name = QTableWidgetItem(sensor["solvent"]["name"])
            cell_additive_name = QTableWidgetItem(sensor["additive"]["name"])

            self.insertRow(row + 1)
            self.setItem(row + 1, 0, cell_idx)
            self.setItem(row + 1, 1, cell_solvent_name)
            self.setItem(row + 1, 2, cell_additive_name)
            self.setCellWidget(row + 1, 3, widget_cb_display)
            self.set_editable(cell_idx, False)
            self.set_editable(cell_solvent_name, False)
            self.set_editable(cell_additive_name, False)

        length = self.horizontalHeader().length() + 2
        if self.verticalScrollBar().isVisible():
            self.setFixedWidth(length + self.scroll_width)
        else:
            self.setFixedWidth(length)

    def set_first_row(self):
        self.insertRow(0)
        cell = QTableWidgetItem()
        self.setSpan(0, 0, 1, 2)
        self.setItem(0, 0, cell)
        self.set_editable(cell, False)

        widget_cb_display_all = QWidget()
        lyt_cb_display_all = QHBoxLayout(widget_cb_display_all)
        lyt_cb_display_all.addWidget(self.cb_display_all)
        lyt_cb_display_all.setAlignment(Qt.AlignCenter)
        lyt_cb_display_all.setContentsMargins(0, 0, 0, 0)
        self.setCellWidget(0, 3, widget_cb_display_all)

    def on_change_display(self, row):
        combination = self.combination
        associations = combination["sensor_associations"]
        idx = associations[row]["idx"]

        indexes = self.display_association_indexes

        if self.check_boxes[row].isChecked():
            if idx not in indexes:
                indexes.append(idx)
                if not self.emit_signal_blocked:
                    self.display_associations_changed.emit(indexes)
        else:
            if idx in indexes:
                indexes.remove(idx)
                if not self.emit_signal_blocked:
                    self.display_associations_changed.emit(indexes)

    def on_display_all_changed(self, value):
        is_checked = self.cb_display_all.isChecked()
        self.emit_signal_blocked = True
        for check_box in self.check_boxes:
            check_box: QCheckBox
            check_box.setChecked(is_checked)

        self.emit_signal_blocked = False
        self.display_associations_changed.emit(self.display_association_indexes)


class SelectCombinationTableController(TableWidgetController):
    display_associations_changed = Signal(list)

    def __init__(self, parent=None, combination_id: int = None):
        self.combination_id = combination_id

        super().__init__(SelectCombinationTableModel, SelectCombinationTableView, parent)

        view: SelectCombinationTableView = self.view
        view.display_associations_changed.connect(self.display_associations_changed.emit)
        self.update_combination()

    def init_controller(self):
        super().init_controller()

    def update_combination(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                combination = json.loads(json_str)["sensor_combination"]

                view: SelectCombinationTableView = self.view
                view.set_table_items(combination)

        self.api_manager.get_sensor_combination(api_handler, self.combination_id)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = SelectCombinationTableController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
