from ui.common import BaseController
from ui.tabs.experiment import ExperimentModel, ExperimentView
from ui.tabs.experiment.explorer.explorer_tree import ExplorerTreeController


class ExperimentController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ExperimentModel, ExperimentView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
