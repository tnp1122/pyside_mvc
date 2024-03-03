from ui.app.main_tab import MainTabModel, MainTabView
from ui.common import TabWidgetController
from ui.tabs.experiment import ExperimentController


class MainTabController(TabWidgetController):
    def __init__(self, parent=None):
        super().__init__(MainTabModel, MainTabView, parent)

    def init_controller(self):
        super().init_controller()

        view: MainTabView = self.view
        experiment: ExperimentController = view.experiment
        experiment.request_add_combination.connect(lambda: view.setCurrentIndex(3))

    def set_first_tab(self, index, switch=True):
        if switch:
            self.view.setCurrentIndex(0)
        self.view.first.set_current_index(index)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MainTabController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
