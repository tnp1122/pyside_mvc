from ui.common import BaseController
from ui.tabs.target_material.target_list_table import TargetListTableModel, TargetListTableView


class TargetListTableController(BaseController):
    def __init__(self, parent=None):
        super().__init__(TargetListTableModel, TargetListTableView, parent)

    def set_table_items(self, target_list):
        self.model.target_list = target_list
        self.view.set_table_items(target_list)

    def cancel_added_items(self):
        self.set_table_items(self.model.target_list)

    def get_new_list(self):
        origin_count = len(self.model.target_list)
        new_target_list = []
        for row in range(origin_count+1, self.view.rowCount()):
            new_target_list.append(self.view.item(row, 0).text())

        return new_target_list


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = TargetListTableController()
    target_list = ["타겟1", "타겟2"]
    widget.set_table_items(target_list)
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
