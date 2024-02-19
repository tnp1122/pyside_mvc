from ui.common import BaseController
from ui.tabs.experiment import ExperimentModel, ExperimentView
from ui.tabs.experiment.window.add_experiment import AddExperimentController
from ui.tabs.experiment.window.add_plate import AddPlateController


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
        add_experiment.experiment_added_signal.connect(lambda controller: self.remove_tab(controller))

    def on_tree_add_button(self, indexes: list):
        if len(indexes) == 2:
            add_plate = AddPlateController()
            self.view.window_widget.add_tab(add_plate.view, "새 플레이트")
            add_plate.plate_added_signal.connect(lambda controller: self.remove_tab(controller))


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
