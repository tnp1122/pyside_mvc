import json
import logging
from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtNetwork import QNetworkReply

from model import Targets
from ui.common import TabWidgetController
from ui.common.confirmation_dialog import ConfirmationDialog
from ui.common.toast import Toast
from ui.tabs.experiment.window.snapshot import PlateSnapshotModel, PlateSnapshotView
from ui.tabs.experiment.window.snapshot.extract import ColorExtractController
from ui.tabs.experiment.window.snapshot.process import SnapshotProcessView
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListView, CaptureListController
from ui.tabs.experiment.window.snapshot.process.unit import PlateCaptureUnitView, PlateCaptureUnitController

from util import SnapshotDataManager

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
        self.snapshot_loaded = False

        super().__init__(PlateSnapshotModel, PlateSnapshotView, parent, snapshot_info)

    def init_controller(self):
        super().init_controller()

        view: PlateSnapshotView = self.view

        plate_process_view: SnapshotProcessView = view.plate_process.view
        view.color_difference.set_snapshot_age(plate_process_view.snapshot_age)
        plate_process_view.snapshot_age_changed.connect(view.color_difference.set_snapshot_age)
        plate_process_view.btn_save.clicked.connect(self.on_save_button_clicked)

        capture_list_view: CaptureListView = view.plate_process.view.capture_list.view
        extract_widget: ColorExtractController = view.color_extract
        capture_list_view.btn_plus.clicked.connect(extract_widget.add_image_shell)
        capture_list_view.mask_changed.connect(lambda index: self.on_mask_changed(index))

        self.update_targets()

    def update_targets(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.targets.set_items_with_json(json_str, "targets")

                view: PlateSnapshotView = self.view
                view.set_targets(self.targets)

                if self.snapshot_id:
                    self.load_snapshot_info()
                    return
                self.snapshot_loaded = True
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_targets(api_handler, self.experiment_id)

    def load_snapshot_info(self):
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
                    sdm = SnapshotDataManager(self.snapshot_path, self.snapshot_age, target_name)
                    cropped_image, mean_color_mask_info, mask = sdm.load_datas()

                    new_unit = capture_list_view.add_new_unit()
                    new_unit.view.set_selected_target(target_index)
                    new_unit.set_snapshot_datas(cropped_image, mean_color_mask_info, mask)

                    extract_widget: ColorExtractController = view.color_extract
                    extract_widget.add_image_shell()

                self.snapshot_loaded = True

                for index in range(len(captures)):
                    self.on_mask_changed(index)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_snapshot(api_handler, self.plate_id, self.snapshot_id)

    def on_mask_changed(self, index):
        if not self.snapshot_loaded:
            return

        view: PlateSnapshotView = self.view
        extract_widget: ColorExtractController = view.color_extract
        capture_list: CaptureListController = view.plate_process.view.capture_list
        capture_list_view: CaptureListView = capture_list.view
        unit: PlateCaptureUnitController = capture_list_view.units[index]
        unit_view: PlateCaptureUnitView = unit.view

        mean_colored_pixmap = unit.mean_colored_pixmap
        cropped_original_pixmap = unit.cropped_original_pixmap
        target_name = unit_view.cmb_target.currentText()

        extract_widget.set_image_shell(index, mean_colored_pixmap, cropped_original_pixmap, target_name)

        view.color_difference.set_color_datas(capture_list)

    def on_save_button_clicked(self):
        view: PlateSnapshotView = self.view
        process_view: SnapshotProcessView = view.plate_process.view
        capture_list_view: CaptureListView = process_view.capture_list.view

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

        dlg_confirm = ConfirmationDialog(
            "스냅샷 저장", "스냅샷 저장후에는 수정이 불가능하며, 삭제만 가능합니다.", "저장", parent=self.view)
        dlg_confirm.confirmed.connect(lambda: self.save_snapshot(captured_at_obj, plate_capture_datas))
        dlg_confirm.exec()

    def save_snapshot(self, captured_at_obj, plate_capture_datas):
        view: PlateSnapshotView = self.view
        process_view: SnapshotProcessView = view.plate_process.view
        capture_list: CaptureListController = process_view.capture_list
        capture_list_view: CaptureListView = capture_list.view

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

                    self.snapshot_id = plate_snapshot["id"]
                    capture_list.set_unit_id(plate_captures)
                    process_view.set_editable(False)
                    self.snapshot_added.emit(snapshot_age)

                    for unit in capture_list_view.units:
                        unit: PlateCaptureUnitController
                        unit_view: PlateCaptureUnitView = unit.view

                        target_name = unit_view.cmb_target.currentText()

                        cropped_image, mean_color_mask_info, mask = unit.get_snapshot_datas()
                        sdm = SnapshotDataManager(self.snapshot_path, snapshot_age, target_name)
                        sdm.save_datas(cropped_image, mean_color_mask_info, mask)

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
