import logging

from PySide6.QtCore import Signal, QObject
from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.common.toast import Toast
from ui.common import BaseController
from ui.tabs.experiment.window.add_experiment.model import AddExperimentModel
from ui.tabs.experiment.window.add_experiment.view import AddExperimentView

WIDGET = "[Add Experiment Controller]"


class AddExperimentController(BaseController):
    api_manager = APIManager()
    experiment_added_signal = Signal(QObject)

    def __init__(self, parent=None):
        super().__init__(AddExperimentModel, AddExperimentView, parent)

    def init_controller(self):
        super().init_controller()

        self.view.et_name.textChanged.connect(lambda value: self.update_experiment_name(value))
        self.view.btn_add.clicked.connect(self.add_experiment)

    def update_experiment_name(self, value):
        self.model.experiment_name = value

    def add_experiment(self):
        experiment = {"name": self.model.experiment_name}

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                self.experiment_added_signal.emit(self)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.add_experiment(api_handler, experiment)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AddExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
