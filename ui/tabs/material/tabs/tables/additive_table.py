from PySide6.QtWidgets import QHeaderView

from ui.common import BaseTableWidgetView, TableWidgetController


class AdditiveTableModel:
    def __init__(self):
        pass


class AdditiveTableView(BaseTableWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setColumnCount(1)

        headers = ["첨가제 종류"]
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class AdditiveTableController(TableWidgetController):
    def __init__(self, parent=None):
        super().__init__(AdditiveTableModel, AdditiveTableView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AdditiveTableController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
