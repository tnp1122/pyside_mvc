from ui.common import TableWidgetController
from ui.tabs.target_material.target_list_table import TargetListTableModel, TargetListTableView


class TargetListTableController(TableWidgetController):
    def __init__(self, parent=None):
        super().__init__(TargetListTableModel, TargetListTableView, parent)


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
