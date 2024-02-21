from ui.common import TabWidgetController
from ui.tabs.experiment.window.snapshot import PlateSnapshotModel, PlateSnapshotView


class PlateSnapshotController(TabWidgetController):
    def __init__(self, parent=None):
        super().__init__(PlateSnapshotModel, PlateSnapshotView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = PlateSnapshotController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
