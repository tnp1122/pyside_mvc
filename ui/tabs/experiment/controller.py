from ui.common import BaseController
from ui.tabs.experiment import ExperimentModel, ExperimentView
from ui.tabs.experiment.window.add_experiment import AddExperimentController


class ExperimentController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ExperimentModel, ExperimentView, parent)

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()
        self.view.explorer.view.btn_add.clicked.connect(self.add_experiment)

    def add_experiment(self):
        add_experiment = AddExperimentController()
        self.view.window_widget.add_tab(add_experiment.view, "새 실험")
        add_experiment.experiment_added_signal.connect(lambda controller: self.update_view(controller))

    def update_view(self, controller: add_experiment):
        self.view.window_widget.remove_tab(controller.view)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
