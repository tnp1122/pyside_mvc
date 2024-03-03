import json
import logging
from datetime import datetime

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtNetwork import QNetworkReply

from ui.common import TabWidgetController
from ui.common.toast import Toast
from ui.tabs.experiment.window.snapshot import PlateSnapshotModel, PlateSnapshotView
from ui.tabs.experiment.window.snapshot.capture import PlateCaptureView
from ui.tabs.experiment.window.snapshot.capture.capture_list import CaptureListView, CaptureListController
from ui.tabs.experiment.window.snapshot.capture.unit import PlateCaptureUnitView, PlateCaptureUnitController

from util import image_converter as ic

WIDGET = "[Plate Snapshot Controller]"


class PlateSnapshotController(TabWidgetController):
    snapshot_added = Signal(int)

    def __init__(self, parent=None, snapshot_info=None):
        self.experiment_id = snapshot_info.pop("experiment_id")
        self.plate_id = snapshot_info.pop("plate_id")
        self.snapshot_path = snapshot_info["snapshot_path"]
        self.plate_made_at = snapshot_info["plate_made_at"]
        self.snapshot_id = snapshot_info["snapshot_id"]
        plate_info = snapshot_info

        self.targets = []

        super().__init__(PlateSnapshotModel, PlateSnapshotView, parent, plate_info)

    def init_controller(self):
        super().init_controller()

        plate_capture_view: PlateCaptureView = self.view.plate_capture.view
        plate_capture_view.btn_save.clicked.connect(self.on_save_button_clicked)

        capture_list_view: CaptureListView = self.view.plate_capture.view.capture_list.view
        capture_list_view.mask_changed.connect(self.on_mask_changed)

        self.update_targets()
        if self.snapshot_id:
            self.update_snapshot()

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

    def update_snapshot(self):
        view: PlateSnapshotView = self.view
        capture_view: PlateCaptureView = view.plate_capture.view

        capture_view.set_et_editable(False)

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                response = json.loads(json_str)["plate_snapshot"]
                capture_view.set_snapshot(response)
            else:
                msg = f"{WIDGET} update_snapshot-{reply.errorString()}"
                logging.error(msg)
                Toast().toast(msg)

        self.api_manager.get_snapshot(api_handler, self.plate_id, self.snapshot_id)

    def set_targets(self, targets):
        self.targets = targets

        view: PlateSnapshotView = self.view
        view.set_targets(targets)

    def on_mask_changed(self):
        view: PlateSnapshotView = self.view
        capture_view: PlateCaptureView = view.plate_capture.view
        capture_list = capture_view.capture_list

        view.color_extract.set_image_list(capture_list)

    def on_save_button_clicked(self):
        view: PlateSnapshotView = self.view

        if self.snapshot_id:
            pass

        else:
            capture_view: PlateCaptureView = view.plate_capture.view
            capture_list: CaptureListController = capture_view.capture_list
            capture_list_view: CaptureListView = capture_list.view

            plate_made_at_obj: datetime = datetime.strptime(self.plate_made_at, "%Y-%m-%dT%H:%M:%S")
            captured_at_obj: datetime = capture_view.captured_at

            time_diff = captured_at_obj - plate_made_at_obj
            plate_age = int(time_diff.total_seconds() / 3600)
            if plate_age < 0:
                msg = "플레이트 촬영 시간은 제작시간 이후여야 합니다."
                Toast().toast(msg)
                logging.error(msg)
                return

            captured_at = captured_at_obj.strftime("%Y-%m-%dT%H:%M:%S")

            target_id_check = []
            plate_capture_datas = []
            for unit in capture_list_view.units:
                unit: PlateCaptureUnitController
                unit_view: PlateCaptureUnitView = unit.view

                if not unit.mean_colors:  # 마스킹 적용된 유닛만 저장됨
                    continue

                target_id = unit_view.get_selected_target_id()
                if target_id in target_id_check:
                    msg = "중복된 타겟 물질을 사용할 수 없습니다."
                    Toast().toast(msg)
                    logging.error(msg)
                    return

                target_id_check.append(target_id)
                plate_capture_data = {"target": target_id, "image_uri": ""}
                plate_capture_datas.append(plate_capture_data)

            if not target_id_check:
                msg = "플레이트를 촬영하세요."
                Toast().toast(msg)
                logging.error(msg)
                return

            plate_snapshot_data = {"captured_at": captured_at, "plate_captures": plate_capture_datas}

            def api_handler(reply):
                if reply.error() == QNetworkReply.NoError:

                    json_str = reply.readAll().data().decode("utf-8")
                    plate_snapshot = json.loads(json_str)["plate_snapshot"]
                    plate_captures = plate_snapshot["plate_captures"]
                    shapshot_age = plate_snapshot["age"]

                    self.snapshot_id = plate_snapshot["id"]
                    capture_list.set_unit_id(plate_captures)
                    capture_view.set_et_editable(False)
                    self.snapshot_added.emit(shapshot_age)

                    for index, unit in enumerate(capture_list_view.units):
                        unit: PlateCaptureUnitController
                        unit_view: PlateCaptureUnitView = unit.view

                        target_name = unit_view.cmb_target.currentText()

                        cropped_image, mean_color_mask_info, masked_array = unit.get_cropped_image_info()

                        _, mcmi_path, npz_path = ic.get_snapshot_path(self.snapshot_path, shapshot_age, target_name)
                        ic.save_plate_snapshot_image_(cropped_image, self.snapshot_path, shapshot_age, target_name)

                        with open(mcmi_path, "w") as mcmi_file:
                            json.dump(mean_color_mask_info, mcmi_file)

                        np.savez_compressed(npz_path, masked_array)


                else:
                    self.api_manager.on_failure(reply)

            self.api_manager.add_snapshot(api_handler, self.plate_id, {"plate_snapshot": plate_snapshot_data})


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = PlateSnapshotController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
