from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtNetwork import QNetworkReply

from ui.common import BaseController
from ui.common.confirmation_dialog import ConfirmationDialog
from ui.common.tree_view import TreeRow, TreeSignalData
from ui.tabs.experiment import ExperimentModel, ExperimentView
from ui.tabs.experiment.explorer import ExplorerController, ExplorerView
from ui.tabs.experiment.window import ExperimentWindowController
from ui.tabs.experiment.window.add_experiment import AddExperimentController
from ui.tabs.experiment.window.add_plate import AddPlateController, AddPlateView
from ui.tabs.experiment.window.snapshot import PlateSnapshotController


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
        tree_root.double_clicked_signal.connect(self.open_snapshot_tab)
        tree_root.remove_signal.connect(self.on_tree_remove_clicked)

        view.window_widget.view.tabCloseRequested.connect(lambda index: self.remove_tab_with_index(index))

    def add_tab(self, controller: BaseController, mode, tab_name):
        self.view.window_widget.add_tab(controller, mode, tab_name)
        self.tabs.append(controller)

    def remove_tab(self, controller: BaseController):
        window_widget: ExperimentWindowController = self.view.window_widget
        window_widget.remove_tab(controller)

    def remove_tab_with_index(self, index):
        self.remove_tab(self.tabs[index])
        del self.tabs[index]

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

            add_plate = AddPlateController()
            add_plate_view: AddPlateView = add_plate.view

            def on_combination_loaded():
                if add_plate_view.cmb_experiment.currentIndex() == experiment_index:
                    add_plate_view.cmb_combination.setCurrentIndex(combination_index)

            add_plate.plate_added_signal.connect(lambda controller: self.on_plate_added(controller))
            add_plate.experiment_loaded.connect(lambda: add_plate_view.cmb_experiment.setCurrentIndex(experiment_index))
            add_plate.combination_loaded.connect(on_combination_loaded)

            self.add_tab(add_plate, 0, "새 플레이트")

        elif depth == 3:
            self.open_snapshot_tab(indexes)

    def open_snapshot_tab(self, indexes: list):
        view: ExperimentView = self.view
        depth = len(indexes)

        experiment_index = indexes[0]
        combination_index = indexes[1]
        plate_index = indexes[2]

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
        else:
            snapshot_index = indexes[3]
            snapshot = plate["plate_snapshots"][snapshot_index]
            snapshot_id = snapshot["id"]
            snapshot_age = snapshot["age"]
            snapshot_captured_at = snapshot["captured_at"]
            tab_name = self.get_tab_name(plate_name, snapshot_age)

        snapshot_info = {"experiment_id": experiment_id, "plate_id": plate["id"], "plate_made_at": plate_made_at,
                         "snapshot_path": snapshot_path, "snapshot_id": snapshot_id, "snapshot_age": snapshot_age,
                         "snapshot_captured_at": snapshot_captured_at}
        plate_snapshot = PlateSnapshotController(snapshot_info=snapshot_info)
        if depth == 3:
            plate_snapshot.snapshot_added.connect(
                lambda snapshot_age: self.on_snapshot_added(plate_snapshot, plate_name, snapshot_age))

        self.add_tab(plate_snapshot, 1, tab_name)

    def on_tree_remove_clicked(self, tree_signal_data: TreeSignalData):
        indexes = tree_signal_data.indexes

        experiment_tree = self.view.explorer.experiment_tree
        experiment, combination, plate, snapshot = None, None, None, None
        experiment_id, combination_id, plate_id, snapshot_id = None, None, None, None

        title, content = "", ""
        cancel_text = "취소"
        has_refer = False
        use_confirm = True

        depth = len(indexes)
        if depth > 0:
            experiment = experiment_tree[indexes[0]]
            experiment_id = experiment["id"]

        if depth > 1:
            combination = experiment["sensor_combinations"][indexes[1]]
            combination_id = combination["id"]

        if depth > 2:
            plate = combination["plates"][indexes[2]]
            plate_id = plate["id"]

        if depth > 3:
            snapshot = plate["plate_snapshots"][indexes[3]]
            snapshot_id = snapshot["id"]

        if depth == 1:
            experiment_name = experiment["name"]
            combinations = experiment["sensor_combinations"]

            title = "실험 삭제"
            content = f"[실험] {experiment_name}을(를) 삭제하시겠습니까?"
            for combination in combinations:
                if combination["plates"]:
                    has_refer = True
                    content = "하위 플레이트를 삭제한 뒤에 실험을 삭제할 수 있습니다."
                    break

        elif depth == 2:
            combination_name = combination["name"]
            plates = combination["plates"]

            title = "조합 삭제"
            content = f"[조합] {combination_name}을(를) 삭제하시겠습니까?"

            if plates:
                has_refer = True
                content = "하위 플레이트를 삭제한 뒤에 센서 조합을 삭제할 수 있습니다."

        elif depth == 3:
            plate_name = plate["name"]
            snapshots = plate["plate_snapshots"]

            title = "플레이트 삭제"
            content = f"[플레이트] {plate_name}을(를) 삭제하시겠습니까?"

            if snapshots:
                has_refer = True
                content = "하위 스냅샷을 삭제한 뒤에 플레이트를 삭제할 수 있습니다."

        elif depth == 4:
            snapshot_age = snapshot["age"]
            snapshot_name = f"{plate['name']}_{snapshot_age}H"

            title = "스냅샷 삭제"
            content = f"[스냅샷] {snapshot_name}을(를) 삭제하시겠습니까?"

        if has_refer:
            cancel_text = "확인"
            use_confirm = False

        dlg_confirm = ConfirmationDialog(
            title, content, cancel_text=cancel_text, use_confirm=use_confirm, parent=self.view)

        dlg_confirm.confirmed.connect(
            lambda: self.remove_tree_item(depth, experiment_id, combination_id, plate_id, snapshot_id))
        dlg_confirm.exec()

    def remove_tree_item(self, depth, experiment_id, combination_id, plate_id, snapshot_id):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                self.view.explorer.update_tree_view()
            else:
                self.api_manager.on_failure(reply)

        if depth == 1:
            self.api_manager.remove_experiment(api_handler, experiment_id)
        elif depth == 2:
            self.api_manager.remove_sensor_combination(api_handler, experiment_id, combination_id)
        elif depth == 3:
            self.api_manager.remove_plate(api_handler, plate_id)
        elif depth == 4:
            self.api_manager.remove_snapshot(api_handler, plate_id, snapshot_id)

    def on_experiment_added(self, controller: AddExperimentController):
        self.view.explorer.update_tree_view()
        self.remove_tab(controller)

    def on_plate_added(self, controller: AddPlateController):
        self.view.explorer.update_tree_view()
        self.remove_tab(controller)

    def on_snapshot_added(self, plate_snapshot: PlateSnapshotController, plate_name, snapshot_age):
        self.view.explorer.update_tree_view()

        tab_name = self.get_tab_name(plate_name, snapshot_age)
        self.view.window_widget.set_tab_name(plate_snapshot, tab_name)

    def get_tab_name(self, plate_name, snapshot_age):
        tab_name = f"{plate_name}_{snapshot_age}H"

        if len(tab_name) > 16:
            tab_name = tab_name[:12] + "..." + tab_name[-3:]

        return tab_name


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
