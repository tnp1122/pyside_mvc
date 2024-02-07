from PySide6.QtWidgets import QHeaderView

from ui.common import BaseTableWidgetView, TableWidgetController


class SolventTableModel:
    def __init__(self):
        pass


class SolventTableView(BaseTableWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setColumnCount(1)

        headers = ["용매 종류"]
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class SolventTableController(TableWidgetController):
    def __init__(self, parent=None):
        super().__init__(SolventTableModel, SolventTableView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = SolventTableController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
