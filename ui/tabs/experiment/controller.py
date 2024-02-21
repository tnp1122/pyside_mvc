from ui.common import BaseController
from ui.tabs.experiment import ExperimentModel, ExperimentView
from ui.tabs.experiment.window.add_experiment import AddExperimentController
from ui.tabs.experiment.window.add_plate import AddPlateController, AddPlateView
from ui.tabs.experiment.window.snapshot import PlateSnapshotController


class ExperimentController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ExperimentModel, ExperimentView, parent)

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()

        view: ExperimentView = self.view
        view.explorer.view.btn_add.clicked.connect(self.add_experiment)
        view.explorer.view.tree.root.clicked_signal.connect(self.on_tree_add_button)

    def remove_tab(self, controller: BaseController):
        self.view.window_widget.remove_tab(controller.view)

    def add_experiment(self):
        add_experiment = AddExperimentController()
        self.view.window_widget.add_tab(add_experiment.view, "새 실험")
        add_experiment.experiment_added_signal.connect(lambda controller: self.on_experiment_added(controller))

    def on_tree_add_button(self, indexes: list):
        if len(indexes) == 2:
            experiment_index = indexes[0]
            combination_index = indexes[1]

            add_plate = AddPlateController()

            def on_combination_loaded():
                view: AddPlateView = add_plate.view
                if view.cmb_experiment.currentIndex() == experiment_index:
                    view.cmb_combination.setCurrentIndex(combination_index)

            add_plate.plate_added_signal.connect(lambda controller: self.on_plate_added(controller))
            add_plate.experiment_loaded.connect(lambda: add_plate.view.cmb_experiment.setCurrentIndex(experiment_index))
            add_plate.combination_loaded.connect(on_combination_loaded)

            self.view.window_widget.add_tab(add_plate.view, "새 플레이트")

        elif len(indexes) == 3:
            experiment_index = indexes[0]
            combination_index = indexes[1]
            plate_index = indexes[2]

            snapshot = PlateSnapshotController()

            self.view.window_widget.add_tab(snapshot.view, "")

    def on_experiment_added(self, controller: AddExperimentController):
        self.view.explorer.update_tree_view()
        self.remove_tab(controller)

    def on_plate_added(self, controller: AddPlateController):
        self.view.explorer.update_tree_view()
        self.remove_tab(controller)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
