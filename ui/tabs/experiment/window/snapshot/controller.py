import json
import logging
from datetime import datetime

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtNetwork import QNetworkReply

from models import Targets
from models.snapshot import Snapshot
from ui.common import TabWidgetController
from ui.common.camera_widget.section_camera_display import SectionCameraDisplay
from ui.common.confirmation_dialog import ConfirmationDialog
from ui.common.toast import Toast
from ui.tabs.experiment.window.snapshot import PlateSnapshotModel, PlateSnapshotView
from ui.tabs.experiment.window.snapshot.difference import ColorDifferenceController
from ui.tabs.experiment.window.snapshot.mean_color import MeanColorView
from ui.tabs.experiment.window.snapshot.mean_color.image_list import ImageListController
from ui.tabs.experiment.window.snapshot.process import SnapshotProcessView
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListView, CaptureListController

WIDGET = "[Plate Snapshot Controller]"


class PlateSnapshotController(TabWidgetController):
    snapshot_added = Signal(int)

    def __init__(self, parent=None, snapshot_info=None):
        self.experiment_id = snapshot_info.pop("experiment_id")
        self.plate_id = snapshot_info.pop("plate_id")
        self.plate_made_at = snapshot_info["plate_made_at"]
        self.snapshot_path = snapshot_info["snapshot_path"]
        self.snapshot_id = snapshot_info["snapshot_id"]
        self.snapshot_age = snapshot_info.pop("snapshot_age")

        self.targets = Targets()
        self.snapshots: list[Snapshot] = []

        super().__init__(PlateSnapshotModel, PlateSnapshotView, parent, snapshot_info)

    def init_controller(self):
        super().init_controller()

        view: PlateSnapshotView = self.view
        plate_process_view: SnapshotProcessView = view.plate_process.view
        section_camera_display: SectionCameraDisplay = plate_process_view.camera_widget.camera_display

        view.color_difference.set_snapshot_age(plate_process_view.snapshot_age)
        plate_process_view.snapshot_age_changed.connect(view.color_difference.set_snapshot_age)
        plate_process_view.btn_save.clicked.connect(self.on_save_button_clicked)
        section_camera_display.lab_correction_factors_set_signal.connect(self.on_lab_correction_factors_set)

        capture_list_view: CaptureListView = view.plate_process.view.capture_list.view
        capture_list_view.btn_plus.clicked.connect(self.add_new_snapshot)

        self.update_targets()

    def update_targets(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.targets.set_items_with_json(json_str, "targets")

                view: PlateSnapshotView = self.view
                view.set_targets(self.targets)

                if self.snapshot_id:
                    self.update_snapshot_info()
                    return
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_targets(api_handler, self.experiment_id)

    def update_snapshot_info(self):
        view: PlateSnapshotView = self.view
        process_view: SnapshotProcessView = view.plate_process.view
        capture_list_view: CaptureListView = process_view.capture_list.view
        capture_list_view.clear()

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                response = json.loads(json_str)["plate_snapshot"]

                captures = response["plate_captures"]
                for index, capture in enumerate(captures):
                    target_id = capture["target"]
                    target_index, target_name = self.targets.item_name_from_id(target_id)

                    new_snapshot: Snapshot = self.add_new_snapshot(target_index)
                    new_snapshot.load_snapshot(self.snapshot_path, self.snapshot_age, target_name)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_snapshot(api_handler, self.plate_id, self.snapshot_id)

    def on_save_button_clicked(self):
        view: PlateSnapshotView = self.view
        process_view: SnapshotProcessView = view.plate_process.view

        plate_made_at_obj: datetime = datetime.strptime(self.plate_made_at, "%Y-%m-%dT%H:%M:%S")
        captured_at_obj: datetime = process_view.captured_at

        time_diff = captured_at_obj - plate_made_at_obj
        snapshot_age = int(time_diff.total_seconds() / 3600)
        if snapshot_age < 0:
            msg = "스냅샷 촬영 시간은 플레이트 제작시간 이후여야 합니다."
            Toast().toast(msg)
            logging.error(msg)
            return

        target_id_check = []
        plate_capture_datas = []

        for snapshot in self.snapshots:
            snapshot: Snapshot
            if snapshot.target is not None:
                target_id = snapshot.target.id
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

        dlg_confirm = ConfirmationDialog(
            "스냅샷 저장", "스냅샷 저장후에는 수정이 불가능하며, 삭제만 가능합니다.", "저장", parent=self.view)
        dlg_confirm.confirmed.connect(lambda: self.save_snapshot(captured_at_obj, plate_capture_datas))
        dlg_confirm.exec()

    def save_snapshot(self, captured_at_obj, plate_capture_datas):
        view: PlateSnapshotView = self.view
        process_view: SnapshotProcessView = view.plate_process.view
        capture_list: CaptureListController = process_view.capture_list

        if self.snapshot_id:
            pass

        else:

            captured_at = captured_at_obj.strftime("%Y-%m-%dT%H:%M:%S")
            plate_snapshot_data = {"captured_at": captured_at, "plate_captures": plate_capture_datas}

            def api_handler(reply):
                if reply.error() == QNetworkReply.NoError:

                    json_str = reply.readAll().data().decode("utf-8")
                    plate_snapshot = json.loads(json_str)["plate_snapshot"]
                    plate_captures = plate_snapshot["plate_captures"]
                    snapshot_age = plate_snapshot["age"]

                    for snapshot in self.snapshots:
                        snapshot: Snapshot
                        snapshot.save_snapshot(self.snapshot_path, snapshot_age)

                    self.snapshot_id = plate_snapshot["id"]
                    capture_list.set_unit_id(plate_captures)
                    process_view.set_editable(False)
                    self.snapshot_added.emit(snapshot_age)

                else:
                    self.api_manager.on_failure(reply)

            self.api_manager.add_snapshot(api_handler, self.plate_id, {"plate_snapshot": plate_snapshot_data})

    def on_lab_correction_factors_set(self, lab_correction_factors: np.ndarray):
        for snapshot in self.snapshots:
            snapshot: Snapshot
            snapshot.update_lab_correction_factors(lab_correction_factors)

        view: PlateSnapshotView = self.view
        mean_color_view: MeanColorView = view.mean_color.view
        mean_color_view.cb_apply_lab_correct.setEnabled(True)
        mean_color_view.cb_apply_lab_correct.setChecked(True)
        mean_color_view.on_cb_apply_lab_correct_changed()

        # image_list: ImageListController = mean_color_view.image_list
        # image_list

    def add_new_snapshot(self, target_index=None) -> Snapshot:
        view: PlateSnapshotView = self.view
        snapshot_instance: Snapshot = view.plate_process.view.camera_widget.status.snapshot_instance
        lab_correction_factors: np.ndarray = snapshot_instance.lab_correction_factors
        use_lab_corrected_pixmap = view.mean_color.view.cb_apply_lab_correct.isChecked()

        new_snapshot = Snapshot()
        if target_index is not None:
            new_snapshot.set_target(self.targets[target_index])
        if lab_correction_factors is not None:
            new_snapshot.update_lab_correction_factors(lab_correction_factors)
            new_snapshot.set_use_lab_corrected_pixmap(use_lab_corrected_pixmap)
        self.snapshots.append(new_snapshot)

        capture_list: CaptureListController = view.plate_process.view.capture_list
        image_list: ImageListController = view.mean_color.view.image_list
        color_difference: ColorDifferenceController = view.color_difference

        capture_list.add_new_unit(new_snapshot)
        image_list.add_new_shell(new_snapshot)
        color_difference.add_new_snapshot(new_snapshot)

        return new_snapshot


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = PlateSnapshotController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
