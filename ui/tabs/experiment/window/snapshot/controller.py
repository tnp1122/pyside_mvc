from ui.common import TabWidgetController
from ui.tabs.experiment.window.snapshot import PlateSnapshotModel, PlateSnapshotView
from ui.tabs.experiment.window.snapshot.capture import PlateCaptureView


class PlateSnapshotController(TabWidgetController):
    def __init__(self, parent=None):
        super().__init__(PlateSnapshotModel, PlateSnapshotView, parent)

    def init_controller(self):
        super().init_controller()

        capture_view: PlateCaptureView = self.view.plate_capture.view
        capture_view.btn_save.clicked.connect(self.on_save_clicked)

    def on_save_clicked(self):
        view: PlateSnapshotView = self.view
        capture_view: PlateCaptureView = self.view.plate_capture.view
        capture_list = capture_view.capture_list

        view.color_extract.set_image_list(capture_list)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = PlateSnapshotController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
