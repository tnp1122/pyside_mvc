import json
from datetime import datetime

from PySide6.QtCore import Signal, QObject
from PySide6.QtNetwork import QNetworkReply

from ui.common import BaseController
from ui.tabs.experiment.window.add_plate import AddPlateModel, AddPlateView


class AddPlateController(BaseController):
    plate_added_signal = Signal(QObject)

    experiments = []
    combinations = []
    experiment_index = -1
    combination_index = -1
    metal_index = -1

    metal_samples = []
    experimenter = ""

    def __init__(self, parent=None):
        super().__init__(AddPlateModel, AddPlateView, parent)

    def init_controller(self):
        super().init_controller()

        view: AddPlateView = self.view
        view.cmb_experiment.currentIndexChanged.connect(self.on_experiment_changed)
        view.cmb_combination.currentIndexChanged.connect(self.on_combination_changed)
        view.cmb_metal.currentIndexChanged.connect(self.on_metal_changed)
        view.et_note.textChanged.connect(self.on_data_changed)
        view.btn_confirm.clicked.connect(self.on_confirm_clicked)

        self.update_experiments()
        self.update_metals()

    def update_experiments(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.experiments = json.loads(json_str)["experiments"]
                self.view.set_experiment_cmb_items(self.experiments)
                self.combinations = [[] for _ in self.experiments]
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_experiments(api_handler)

    def on_experiment_changed(self, event):
        if event > -1:
            if self.experiments:
                self.experiment_index = event
                if len(self.combinations) > event and self.combinations[event]:
                    self.view.set_combination_cmb_items(self.combinations[self.experiment_index])
                else:
                    self.update_combinations()

    def on_combination_changed(self, event):
        if event > -1:
            self.combination_index = event
            self.on_data_changed()

    def on_metal_changed(self, event):
        if event > -1:
            self.metal_index = event
            self.on_data_changed()

    def update_combinations(self):
        ex_index = self.experiment_index

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                combination = json.loads(json_str)["sensor_combinations"]
                self.combinations[ex_index] = combination
                self.view.set_combination_cmb_items(self.combinations[ex_index])
            else:
                self.api_manager.on_failure(reply)

        experiment_id = self.experiments[ex_index]["id"]
        self.api_manager.get_sensor_combination(api_handler, experiment_id)

    def update_metals(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                response = json.loads(json_str)["metal_samples"]
                use_metal_samples = self.setting_manager.get_use_metal_samples()
                metal_samples = []
                for metal_sample in response:
                    if metal_sample["id"] in use_metal_samples:
                        metal_samples.append(metal_sample)

                self.metal_samples = metal_samples
                self.view.set_metal_cmb_items(self.metal_samples)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_metal_samples(api_handler)

    def on_data_changed(self):
        self.view.set_plate_name()

    def on_confirm_clicked(self):
        view: AddPlateView = self.view

        metal = self.metal_samples[self.metal_index]
        metal_made_at = metal["made_at"]
        metal_made_at_object = datetime.strptime(metal_made_at, "%Y-%m-%dT%H:%M:%S")

        date_str = view.lb_date.text()
        hour_str = view.et_time.text()
        datetime_str = f"{date_str}_{hour_str}0000"
        datetime_object = datetime.strptime(datetime_str, "%y%m%d_%H%M%S")

        metal_age_object = datetime_object - metal_made_at_object
        metal_age = int(metal_age_object.total_seconds() / 3600)

        name = view.lb_plate_name.text()
        additive_samples = list(self.setting_manager.get_use_additive_samples())
        combination_id = self.combinations[self.experiment_index][self.combination_index]["id"]
        metal_id = metal["id"]
        made_at = datetime_object.strftime('%Y-%m-%dT%H:%M:%S')

        plate = {
            "name": name,
            "additive_samples": additive_samples,
            "sensor_combination": combination_id,
            "metal_sample": metal_id,
            "metal_age": metal_age,
            "made_at": made_at
        }

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                self.plate_added_signal.emit(self)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.add_plate(api_handler, {"plate": plate})


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AddPlateController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
