from ui.common import BaseController
from ui.tabs.experiment import ExperimentModel, ExperimentView
from ui.tabs.experiment.explorer import ExplorerController
from ui.tabs.experiment.window import ExperimentWindowController
from ui.tabs.experiment.window.add_experiment import AddExperimentController
from ui.tabs.experiment.window.add_plate import AddPlateController, AddPlateView
from ui.tabs.experiment.window.snapshot import PlateSnapshotController


class ExperimentController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ExperimentModel, ExperimentView, parent)

        self.tabs = []

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()

        view: ExperimentView = self.view
        view.explorer.view.btn_add.clicked.connect(self.add_experiment)
        view.explorer.view.tree.root.clicked_signal.connect(self.on_tree_add_button)

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

    def on_tree_add_button(self, indexes: list):
        view: ExperimentView = self.view

        if len(indexes) == 2:
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

        elif len(indexes) == 3:
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

            snapshot_info = {"experiment_id": experiment_id, "plate_id": plate["id"], "snapshot_id": None,
                             "plate_made_at": plate_made_at, "snapshot_path": snapshot_path}
            plate_snapshot = PlateSnapshotController(snapshot_info=snapshot_info)
            plate_snapshot.snapshot_added.connect(
                lambda plate_age: self.on_snapshot_added(plate_snapshot, plate_name, plate_age))

            self.add_tab(plate_snapshot, 1, "새 스냅샷")

    def on_experiment_added(self, controller: AddExperimentController):
        self.view.explorer.update_tree_view()
        self.remove_tab(controller)

    def on_plate_added(self, controller: AddPlateController):
        self.view.explorer.update_tree_view()
        self.remove_tab(controller)

    def on_snapshot_added(self, plate_snapshot: PlateSnapshotController, plate_name, plate_age):
        explorer: ExplorerController = self.view.explorer

        explorer.update_tree_view()

        tab_name = f"{plate_name}_{plate_age}H"

        if len(tab_name) > 16:
            tab_name = tab_name[:12] + "..." + tab_name[-3:]

        self.view.window_widget.set_tab_name(plate_snapshot, tab_name)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
