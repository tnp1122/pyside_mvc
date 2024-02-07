from PySide6.QtWidgets import QHeaderView

from ui.common import BaseTableWidgetView, TableWidgetController


class MetalTableModel:
    def __init__(self):
        pass


class MetalTableView(BaseTableWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setColumnCount(1)

        headers = ["금속 종류"]
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class MetalTableController(TableWidgetController):
    def __init__(self, parent=None):
        super().__init__(MetalTableModel, MetalTableView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MetalTableController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
