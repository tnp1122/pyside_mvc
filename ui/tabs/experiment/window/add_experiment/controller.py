import logging

from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.common.toast import Toast
from ui.common import BaseController
from ui.tabs.experiment.window.add_experiment.model import AddExperimentModel
from ui.tabs.experiment.window.add_experiment.view import AddExperimentView

WIDGET = "[Add Experiment Controller]"


class AddExperimentController(BaseController):
    api_manager = APIManager()

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
                json_str = reply.readAll().data().decode("utf-8")
                print(f"실험 추가 응답: {json_str}")
            else:
                logging.error(f"{WIDGET} add_experiment-{reply.errorString()}")
                Toast().toast(reply.errorString())

        self.api_manager.add_experiment(experiment, api_handler)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AddExperimentController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
