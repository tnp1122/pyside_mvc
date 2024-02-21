from PySide6.QtCore import QSignalMapper, Qt
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout

from ui.common import BaseTableWidgetView
from util.setting_manager import SettingManager


class TargetTableView(BaseTableWidgetView):
    setting_manager = SettingManager()

    targets = []
    experiment_id = -1
    use_target_ids = set()

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        headers = ["타겟 물질", "사용"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def set_table_items(self, items):
        self.clear_table()

        self.targets = items
        self.mapper_change_use = QSignalMapper(self)
        self.mapper_change_use.mappedInt.connect(self.on_change_use)

        for row, item in enumerate(items):
            self.insertRow(row)

            target_id = item["id"]
            name = QTableWidgetItem(item["name"])

            cb_use = QCheckBox()
            if target_id in self.use_target_ids:
                cb_use.setChecked(True)

            cb_use.stateChanged.connect(self.mapper_change_use.map)
            self.mapper_change_use.setMapping(cb_use, row)
            widget_cb_use = QWidget()
            lyt_cb_use = QHBoxLayout(widget_cb_use)
            lyt_cb_use.addWidget(cb_use)
            lyt_cb_use.setAlignment(Qt.AlignCenter)
            lyt_cb_use.setContentsMargins(0, 0, 0, 0)

            self.setItem(row, 0, name)
            self.setCellWidget(row, 1, widget_cb_use)
            self.set_editable(name)

        self.set_add_button()

    def add_new_row(self):
        super().add_new_row()

        count = self.rowCount() - 1
        empty_widget = QTableWidgetItem("")
        self.set_editable(empty_widget, False)
        self.setItem(count, 1, empty_widget)

    def update_experiment_id(self, experiment_id):
        self.experiment_id = experiment_id
        self.use_target_ids = self.setting_manager.get_use_targets(experiment_id)

    def on_change_use(self, row):
        target_id = self.targets[row]["id"]
        cell_check = self.cellWidget(row, 1)
        check_box: QCheckBox = cell_check.layout().itemAt(0).widget()
        is_checked = check_box.isChecked()

        if is_checked:
            self.use_target_ids.add(target_id)
        else:
            if target_id in self.use_target_ids:
                self.use_target_ids.remove(target_id)

        self.setting_manager.set_use_targets(self.experiment_id, self.use_target_ids)
