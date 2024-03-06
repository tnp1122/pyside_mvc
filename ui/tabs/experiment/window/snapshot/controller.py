import json
import logging
import os
from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtNetwork import QNetworkReply

from ui.common import TabWidgetController
from ui.common.toast import Toast
from ui.tabs.experiment.window.snapshot import PlateSnapshotModel, PlateSnapshotView
from ui.tabs.experiment.window.snapshot.process import PlateProcessView
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListView, CaptureListController
from ui.tabs.experiment.window.snapshot.process.unit import PlateCaptureUnitView, PlateCaptureUnitController

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

        self.targets = []

        super().__init__(PlateSnapshotModel, PlateSnapshotView, parent, snapshot_info)

    def init_controller(self):
        super().init_controller()

        view: PlateSnapshotView = self.view

        plate_process_view: PlateProcessView = view.plate_process.view
        plate_process_view.plate_age_changed.connect(view.color_difference.set_plate_age)
        plate_process_view.btn_save.clicked.connect(self.on_save_button_clicked)

        capture_list_view: CaptureListView = view.plate_process.view.capture_list.view
        capture_list_view.mask_changed.connect(self.on_mask_changed)

        self.update_targets()

    def update_targets(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                response = json.loads(json_str)["targets"]
                self.set_targets(response)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_targets(api_handler, self.experiment_id)

    def set_targets(self, targets):
        self.targets = targets

        view: PlateSnapshotView = self.view
        view.set_targets(targets)

    def on_mask_changed(self):
        view: PlateSnapshotView = self.view
        process_view: PlateProcessView = view.plate_process.view
        capture_list = process_view.capture_list

        view.color_extract.set_image_list(capture_list)
        if len(capture_list.view.units) > 1:
            view.color_difference.set_color_datas(capture_list)

    def on_save_button_clicked(self):
        view: PlateSnapshotView = self.view

        return

        if self.snapshot_id:
            pass

        else:
            process_view: PlateProcessView = view.plate_process.view
            capture_list: CaptureListController = process_view.capture_list
            capture_list_view: CaptureListView = capture_list.view

            plate_made_at_obj: datetime = datetime.strptime(self.plate_made_at, "%Y-%m-%dT%H:%M:%S")
            captured_at_obj: datetime = process_view.captured_at

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
                    plate_age = plate_snapshot["age"]

                    self.snapshot_id = plate_snapshot["id"]
                    capture_list.set_unit_id(plate_captures)
                    process_view.set_et_editable(False)
                    self.snapshot_added.emit(plate_age)

                    for index, unit in enumerate(capture_list_view.units):
                        unit: PlateCaptureUnitController
                        unit_view: PlateCaptureUnitView = unit.view

                        target_name = unit_view.cmb_target.currentText()

                        cropped_image, mean_color_mask_info = unit.get_cropped_image_info()
                        image_path = ic.save_plate_snapshot_image(cropped_image, self.snapshot_path, plate_age,
                                                                  target_name)

                        file_name, _ = os.path.splitext(image_path)
                        data_name = file_name + ".mcmi"

                        with open(data_name, "w") as data_file:
                            json.dump(mean_color_mask_info, data_file)

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
