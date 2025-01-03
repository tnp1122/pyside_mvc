from models.snapshot import Snapshot
from ui.common import BaseController
from ui.common.toast import Toast
from ui.tabs.experiment.window.snapshot.difference import ColorDifferenceModel, ColorDifferenceView
from ui.tabs.experiment.window.snapshot.difference.difference_table import ColorDifferenceTableView
from ui.tabs.experiment.window.snapshot.difference.excel_manager import ExcelManager


class ColorDifferenceController(BaseController):
    def __init__(self, parent=None, snapshot_info=None):
        self.snapshot_path = snapshot_info["snapshot_path"]
        self.snapshot_age = 0

        super().__init__(ColorDifferenceModel, ColorDifferenceView, parent)

    def init_controller(self):
        super().init_controller()

        view: ColorDifferenceView = self.view

        view.cmb_control.currentIndexChanged.connect(lambda index: self.on_cmb_control_changed(index))
        view.cmb_target.currentIndexChanged.connect(lambda index: self.on_cmb_target_changed(index))
        view.radio.selected.connect(lambda index: self.on_radio_select_changed(index))
        view.btn_to_excel.clicked.connect(self.to_excel)

    def set_snapshot_age(self, age):
        self.snapshot_age = age

    def on_cmb_control_changed(self, index):
        self.model.control_index = index
        self.update_table_color_datas()

    def on_cmb_target_changed(self, index):
        self.model.target_index = index
        self.update_table_color_datas()

    def on_radio_select_changed(self, index):
        self.model.color_index = index
        self.update_table_color_datas()

    def update_table_color_datas(self):
        model: ColorDifferenceModel = self.model
        view: ColorDifferenceView = self.view
        table_view: ColorDifferenceTableView = view.table.view

        enable_check = 0
        for snapshot in model.snapshots:
            snapshot: Snapshot
            if snapshot.mask_editable or snapshot.snapshot_loaded:
                enable_check += 1
        if enable_check < 2:
            return

        color_type = model.get_selected_color_type()
        target_colors, control_colors, differences = model.get_color_datas(color_type)

        colors_with_differences = [[0] * 7 for _ in range(96)]
        for i in range(96):
            colors_with_differences[i][:3] = target_colors[i]
            colors_with_differences[i][3:6] = control_colors[i]
            colors_with_differences[i][6] = differences[i]

        table_view.set_headers(model.get_headers(color_type))
        table_view.set_table_items(colors_with_differences)

    def add_new_snapshot(self, snapshot: Snapshot):
        model: ColorDifferenceModel = self.model
        model.snapshots.append(snapshot)

        self.set_cmb_items()
        snapshot.target_changed.connect(self.set_cmb_items)
        snapshot.processed.connect(self.update_table_color_datas)

    def set_cmb_items(self):
        model: ColorDifferenceModel = self.model
        view: ColorDifferenceView = self.view

        view.cmb_target.clear()
        view.cmb_control.clear()
        for target in model.targets:
            view.cmb_target.addItem(target.name)
            view.cmb_control.addItem(target.name)

    def to_excel(self):
        model: ColorDifferenceModel = self.model

        em = ExcelManager(self.snapshot_path, self.snapshot_age, model)

        for index in range(len(model.targets)):
            em.save_target_colors(index)
        Toast().toast("저장 완료")


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ColorDifferenceController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
