from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List

from PySide6.QtCore import Signal
from PySide6.QtNetwork import QNetworkReply

from models import Target
from ui.common import BaseController
from ui.common.confirmation_dialog import ConfirmationDialog
from ui.common.tree_view import TreeRow, TreeSignalData
from ui.tabs.experiment import ExperimentModel, ExperimentView
from ui.tabs.experiment.explorer import ExplorerController, ExplorerView
from ui.tabs.experiment.window import ExperimentWindowController
from ui.tabs.experiment.window.add_experiment import AddExperimentController
from ui.tabs.experiment.window.add_plate import AddPlateController, AddPlateView
from ui.tabs.experiment.window.snapshot import PlateSnapshotController
from ui.tabs.experiment.window.timeline import PlateTimelineController


@dataclass
class TreeBranches:
    depth: Optional[int] = None
    experiment_id: Optional[int] = None
    combination_id: Optional[int] = None
    timeline_id: Optional[int] = None
    plate_id: Optional[int] = None
    snapshot_id: Optional[int] = None
    experiment_name: Optional[str] = None
    combination_name: Optional[str] = None
    timeline_name: Optional[str] = None
    plate_name: Optional[str] = None
    snapshot_name: Optional[str] = None
    combinations: Optional[List[Dict]] = None
    timelines: Optional[List[Dict]] = None
    plates: Optional[List[Dict]] = None
    snapshots: Optional[List[Dict]] = None

    @classmethod
    def from_tree_data(cls, experiment_tree: Dict, tree_signal_data: 'TreeSignalData') -> 'TreeBranches':
        indexes = tree_signal_data.indexes
        signal_type = tree_signal_data.type

        instance = cls()
        instance.depth = len(indexes)

        if instance.depth > 0:
            experiment = experiment_tree[indexes[0]]
            instance.experiment_id = experiment["id"]
            instance.experiment_name = experiment["name"]
            instance.combinations = experiment["sensor_combinations"]

        if instance.depth > 1:
            combination = instance.combinations[indexes[1]]
            instance.combination_id = combination["id"]
            instance.combination_name = combination["name"]
            instance.plates = combination["plates"]
            instance.timelines = combination["timelines"]

        if instance.depth > 2 and (signal_type == "plate" or signal_type == "snapshot"):
            plate = instance.plates[indexes[2]]
            instance.plate_id = plate["id"]
            instance.plate_name = plate["name"]
            instance.snapshots = plate["plate_snapshots"]

        if instance.depth > 3:
            if signal_type == "snapshot":
                snapshot = instance.snapshots[indexes[3]]
                snapshot_age = snapshot["age"]
                instance.snapshot_id = snapshot["id"]
                instance.snapshot_name = f"{instance.plate_name}_{snapshot_age}H"
            else:
                timeline = instance.timelines[indexes[3]]
                instance.timeline_id = timeline["id"]
                instance.timeline_name = timeline["name"]

        return instance


class ExperimentController(BaseController):
    request_add_combination = Signal()

    def __init__(self, parent=None):
        super().__init__(ExperimentModel, ExperimentView, parent)

        self.tabs = []

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()

        view: ExperimentView = self.view
        explorer_view: ExplorerView = view.explorer.view
        tree_root: TreeRow = explorer_view.tree.root

        explorer_view.btn_add.clicked.connect(self.add_experiment)
        tree_root.add_signal.connect(self.on_tree_add_button)
        tree_root.double_clicked_signal.connect(self.on_child_double_clicked)
        tree_root.remove_signal.connect(self.on_tree_remove_clicked)

        view.window_widget.view.tabCloseRequested.connect(lambda index: self.remove_tab_with_index(index))

    def add_tab(self, controller: BaseController, mode, tab_name, truncated_name=None):
        if truncated_name is None:
            truncated_name = tab_name
        view: ExperimentView = self.view

        view.window_widget.add_tab(controller, mode, tab_name, truncated_name)
        self.tabs.append(controller)

    def remove_tab(self, controller: BaseController):
        window_widget: ExperimentWindowController = self.view.window_widget
        window_widget.remove_tab(controller)
        self.tabs.remove(controller)

    def remove_tab_with_index(self, index):
        self.remove_tab(self.tabs[index])

    def add_experiment(self):
        add_experiment = AddExperimentController()
        add_experiment.experiment_added_signal.connect(lambda controller: self.on_experiment_added(controller))

        self.add_tab(add_experiment, 0, "새 실험")

    def on_tree_add_button(self, tree_signal_data: TreeSignalData):
        indexes = tree_signal_data.indexes

        depth = len(indexes)

        if depth == 1:
            self.request_add_combination.emit()

        elif depth == 2:
            experiment_index = indexes[0]
            combination_index = indexes[1]

            if tree_signal_data.type == "timeline":
                add_plate = AddPlateController(add_timeline=True)
                tab_name = "새 촬영"
            else:
                add_plate = AddPlateController()
                tab_name = "새 플레이트"
            add_plate_view: AddPlateView = add_plate.view

            def on_combination_loaded():
                if add_plate_view.cmb_experiment.currentIndex() == experiment_index:
                    add_plate_view.cmb_combination.setCurrentIndex(combination_index)

            add_plate.plate_added_signal.connect(lambda controller: self.on_plate_added(controller))
            add_plate.timeline_added_signal.connect(lambda controller: self.on_plate_added(controller))
            add_plate.experiment_loaded.connect(lambda: add_plate_view.cmb_experiment.setCurrentIndex(experiment_index))
            add_plate.combination_loaded.connect(on_combination_loaded)

            self.add_tab(add_plate, 0, tab_name)

        elif depth == 3:
            self.open_snapshot_tab(tree_signal_data)

    def on_child_double_clicked(self, tree_signal_data: TreeSignalData):
        if tree_signal_data.type == "open_timeline":
            self.open_timeline_tab(tree_signal_data)
        else:
            self.open_snapshot_tab(tree_signal_data)

    def open_timeline_tab(self, tree_signal_data: TreeSignalData):
        indexes = tree_signal_data.indexes
        view: ExperimentView = self.view

        experiment_index = indexes[0]
        combination_index = indexes[1]
        timeline_index = indexes[3]

        explorer: ExplorerController = view.explorer
        experiment = explorer.experiment_tree[experiment_index]
        combination = experiment["sensor_combinations"][combination_index]
        timeline = combination["timelines"][timeline_index]

        experiment_name = experiment["name"]
        combination_id = combination["id"]
        combination_name = combination["name"]
        timeline_name = timeline["name"]

        target_data = timeline["target"]
        target = Target(target_data["id"], target_data["name"])
        timeline_path = "\\".join([experiment_name, combination_name, 'timelines', timeline_name])

        args = {"combination_id": combination_id, "timeline_path": timeline_path, "target": target}
        plate_timeline = PlateTimelineController(args=args)
        truncated_name = self.truncate_str(timeline_name)
        self.add_tab(plate_timeline, 1, timeline_name, truncated_name)

    def open_snapshot_tab(self, tree_signal_data: TreeSignalData):
        indexes = tree_signal_data.indexes

        view: ExperimentView = self.view
        depth = len(indexes)

        experiment_index = indexes[0]
        combination_index = indexes[1]
        plate_index = indexes[2] - 1

        explorer: ExplorerController = view.explorer
        experiment = explorer.experiment_tree[experiment_index]
        combination = experiment["sensor_combinations"][combination_index]
        plate = combination["plates"][plate_index]

        experiment_id = experiment["id"]
        experiment_name = experiment["name"]
        combination_name = combination["name"]
        plate_name = plate["name"]
        plate_made_at = plate["made_at"]

        snapshot_path = "\\".join([experiment_name, combination_name, plate_name])

        if depth == 3:
            snapshot_id = None
            snapshot_age = None
            snapshot_captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            tab_name = "새 스냅샷"
            truncated_name = None
        else:
            snapshot_index = indexes[3]
            snapshot = plate["plate_snapshots"][snapshot_index]
            snapshot_id = snapshot["id"]
            snapshot_age = snapshot["age"]
            snapshot_captured_at = snapshot["captured_at"]
            tab_name, truncated_name = self.get_snapshot_tab_name(plate_name, snapshot_age)

        snapshot_info = {"experiment_id": experiment_id, "plate_id": plate["id"], "plate_made_at": plate_made_at,
                         "snapshot_path": snapshot_path, "snapshot_id": snapshot_id, "snapshot_age": snapshot_age,
                         "snapshot_captured_at": snapshot_captured_at}
        plate_snapshot = PlateSnapshotController(snapshot_info=snapshot_info)
        if depth == 3:
            plate_snapshot.snapshot_added.connect(
                lambda snapshot_age: self.on_snapshot_added(plate_snapshot, plate_name, snapshot_age))

        self.add_tab(plate_snapshot, 1, tab_name, truncated_name)

    def on_tree_remove_clicked(self, tree_signal_data: TreeSignalData):
        experiment_tree = self.view.explorer.experiment_tree
        signal_type = tree_signal_data.type
        tree_branches = TreeBranches.from_tree_data(experiment_tree, tree_signal_data)
        depth = tree_branches.depth

        title, content = "", ""
        cancel_text = "취소"
        has_refer = False
        use_confirm = True

        if depth == 1:
            title = "실험 삭제"
            content = f"[실험] {tree_branches.experiment_name}을(를) 삭제하시겠습니까?"
            for combination in tree_branches.combinations:
                if combination["plates"]:
                    has_refer = True
                    content = "하위 플레이트를 삭제한 뒤에 실험을 삭제할 수 있습니다."
                    break

        elif depth == 2:
            title = "조합 삭제"
            content = f"[조합] {tree_branches.combination_name}을(를) 삭제하시겠습니까?"

            if tree_branches.plates:
                has_refer = True
                content = "하위 플레이트를 삭제한 뒤에 센서 조합을 삭제할 수 있습니다."
            elif tree_branches.timelines:
                has_refer = True
                content = "하위 연속촬영을 삭제한 뒤에 센서 조합을 삭제할 수 있습니다."

        elif depth == 3:
            title = "플레이트 삭제"
            content = f"[플레이트] {tree_branches.plate_name}을(를) 삭제하시겠습니까?"

            if tree_branches.snapshots:
                has_refer = True
                content = "하위 스냅샷을 삭제한 뒤에 플레이트를 삭제할 수 있습니다."

        elif depth == 4:
            if signal_type == "timeline":
                title = "연속촬영 삭제"
                content = f"[연속촬영] {tree_branches.timeline_name}을(를) 삭제하시겠습니까?"

            else:
                title = "스냅샷 삭제"
                content = f"[스냅샷] {tree_branches.snapshot_name}을(를) 삭제하시겠습니까?"

        if has_refer:
            cancel_text = "확인"
            use_confirm = False

        dlg_confirm = ConfirmationDialog(
            title, content, cancel_text=cancel_text, use_confirm=use_confirm, parent=self.view)

        dlg_confirm.confirmed.connect(lambda: self.remove_tree_item(tree_branches))
        dlg_confirm.exec()

    # def remove_tree_item(self, depth, experiment_id, combination_id, plate_id, snapshot_id, timeline_id, indexes):
    def remove_tree_item(self, tree_branches: TreeBranches):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                self.view.explorer.update_tree_view()
            else:
                self.api_manager.on_failure(reply)

        depth = tree_branches.depth
        experiment_id = tree_branches.experiment_id
        combination_id = tree_branches.combination_id
        timeline_id = tree_branches.timeline_id
        plate_id = tree_branches.plate_id
        snapshot_id = tree_branches.snapshot_id

        if depth == 1:
            self.api_manager.remove_experiment(api_handler, experiment_id)
        elif depth == 2:
            self.api_manager.remove_sensor_combination(api_handler, experiment_id, combination_id)
        elif depth == 3:
            self.api_manager.remove_plate(api_handler, plate_id)
        elif depth == 4:
            if timeline_id is not None:
                self.api_manager.remove_timeline(api_handler, timeline_id)
            else:
                self.api_manager.remove_snapshot(api_handler, plate_id, snapshot_id)

    def on_experiment_added(self, controller: AddExperimentController):
        self.view.explorer.update_tree_view()
        self.remove_tab(controller)

    def on_plate_added(self, controller: AddPlateController):
        self.view.explorer.update_tree_view()
        self.remove_tab(controller)

    def on_snapshot_added(self, plate_snapshot: PlateSnapshotController, plate_name, snapshot_age):
        self.view.explorer.update_tree_view()

        tab_name, truncated_name = self.get_snapshot_tab_name(plate_name, snapshot_age)
        self.view.window_widget.set_tab_name(plate_snapshot, tab_name, truncated_name)

    def get_snapshot_tab_name(self, plate_name, snapshot_age):
        tab_name = f"{plate_name}_{snapshot_age}H"

        return tab_name, self.truncate_str(tab_name)

    def truncate_str(self, value: str, max_len=16):
        if len(value) > max_len:
            value = value[:max_len - 4] + "..." + value[-3:]

        return value


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
