from ui.common import TableWidgetController
from ui.tabs.experiment.window.snapshot.difference.difference_table import ColorDifferenceTableModel, \
    ColorDifferenceTableView


class ColorDifferenceTableController(TableWidgetController):
    def __init__(self, parent=None):
        super().__init__(ColorDifferenceTableModel, ColorDifferenceTableView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ColorDifferenceTableController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
