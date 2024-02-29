import json
import logging

from PySide6.QtNetwork import QNetworkReply

from ui.common import TabWidgetController
from ui.common.toast import Toast
from ui.tabs.experiment.window.snapshot import PlateSnapshotModel, PlateSnapshotView
from ui.tabs.experiment.window.snapshot.capture import PlateCaptureView
from ui.tabs.experiment.window.snapshot.capture.capture_list import CaptureListView

WIDGET = "[Plate Snapshot Controller]"


class PlateSnapshotController(TabWidgetController):
    def __init__(self, parent=None, snapshot_info=None):
        self.experiment_id = snapshot_info.pop("experiment_id")
        plate_info = snapshot_info

        self.targets = []

        super().__init__(PlateSnapshotModel, PlateSnapshotView, parent, plate_info)

    def init_controller(self):
        super().init_controller()

        capture_list_view: CaptureListView = self.view.plate_capture.view.capture_list.view
        capture_list_view.mask_applied.connect(self.on_mask_applied)

        self.update_targets()

    def update_targets(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                response = json.loads(json_str)["targets"]
                self.set_targets(response)
            else:
                msg = f"{WIDGET} update_targets-{reply.errorString()}"
                logging.error(msg)
                Toast().toast(msg)

        self.api_manager.get_targets(api_handler, self.experiment_id)

    def set_targets(self, targets):
        self.targets = targets

        target_names = []
        for target in targets:
            target_names.append(target["name"])

        view: PlateSnapshotView = self.view
        view.set_target_names(target_names)

    def on_mask_applied(self):
        view: PlateSnapshotView = self.view
        capture_view: PlateCaptureView = view.plate_capture.view
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
