import logging

from models import Image
from ui.common import BaseController
from ui.common.toast import Toast
from ui.tabs.experiment.window.snapshot.process import SnapshotProcessModel, SnapshotProcessView
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListView, CaptureListController
from util.camera_manager import CameraManager


class SnapshotProcessController(BaseController):
    def __init__(self, parent=None, snapshot_info=None):
        super().__init__(SnapshotProcessModel, SnapshotProcessView, parent, snapshot_info)

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()

        view: SnapshotProcessView = self.view
        view.btn_capture.clicked.connect(self.on_capture_clicked)

    def on_capture_clicked(self):
        capture_list_view: CaptureListView = self.view.capture_list.view
        capture_list: CaptureListController = self.view.capture_list
        camera_manager = CameraManager()

        if capture_list_view.units:
            try:
                image = camera_manager.get_current_image()
            except Exception:
                image = None

            if image is not None:
                capture_list.set_unit_image(Image(image, True))
            else:
                msg = "카메라 상태를 확인하세요."
                Toast().toast(msg)
                logging.error(msg)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = SnapshotProcessController()
    widget.late_init()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
