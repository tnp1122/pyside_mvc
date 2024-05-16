import json
from datetime import datetime

from PySide6.QtCore import Signal, QObject
from PySide6.QtNetwork import QNetworkReply

from model import Targets, Experiments, Combinations, Materials
from model.api.metal_sample import MetalSamples
from ui.common import BaseController
from ui.tabs.experiment.window.add_plate import AddPlateModel, AddPlateView


class AddPlateController(BaseController):
    experiment_loaded = Signal()
    combination_loaded = Signal()
    plate_added_signal = Signal(QObject)
    timeline_added_signal = Signal(QObject)

    experimenter = ""

    def __init__(self, parent=None, add_timeline=False):
        super().__init__(AddPlateModel, AddPlateView, parent, add_timeline)
        self.add_timeline = add_timeline

    def init_controller(self):
        super().init_controller()

        self.experiment_index = -1
        self.metal_index = -1
        self.combination_index = -1
        self.target_index = -1

        self.experiments = Experiments()
        self.metal_samples = MetalSamples()
        self.combinationsList = []
        self.targetsList = []
        self.materials = Materials()

        view: AddPlateView = self.view
        view.cmb_experiment.currentIndexChanged.connect(self.on_experiment_changed)
        view.cmb_metal.currentIndexChanged.connect(self.on_metal_changed)
        view.cmb_target.currentIndexChanged.connect(self.on_target_changed)
        view.cmb_combination.currentIndexChanged.connect(self.on_combination_changed)
        view.et_note.textChanged.connect(self.on_data_changed)
        view.btn_confirm.clicked.connect(self.on_confirm_clicked)

        self.update_experiments()
        self.update_metals()

    def on_experiment_changed(self, event):
        if event > -1:
            if self.experiments:
                self.experiment_index = event
                if len(self.combinationsList) > event and self.combinationsList[event]:
                    self.view.set_combination_cmb_items(self.combinationsList[self.experiment_index])
                else:
                    self.update_combinations()
                if len(self.targetsList) > event and self.targetsList[event]:
                    self.view.set_target_cmb_items(self.targetsList[self.experiment_index])
                else:
                    self.update_targets()

    def on_metal_changed(self, event):
        if event > -1:
            self.metal_index = event
            self.on_data_changed()

    def on_target_changed(self, event):
        if event > -1:
            self.target_index = event
            self.on_data_changed()

    def on_combination_changed(self, event):
        if event > -1:
            self.combination_index = event
            self.on_data_changed()

    def update_experiments(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.experiments.set_items_with_json(json_str, "experiments")
                self.view.set_experiment_cmb_items(self.experiments)

                self.combinationsList.clear()
                self.combinationsList.extend([Combinations() for _ in self.experiments])
                self.targetsList.clear()
                self.targetsList.extend([Targets() for _ in self.experiments])

                self.experiment_loaded.emit()
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_experiments(api_handler)

    def update_metals(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.metal_samples.set_sample_items_with_json("metal", json_str, "metal_samples")
                self.view.set_metal_cmb_items(self.metal_samples.using_metal_samples)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_metal_samples(api_handler)

    def update_combinations(self):
        ex_index = self.experiment_index

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                combinations: Combinations = self.combinationsList[ex_index]
                combinations.set_items_with_json(json_str, "sensor_combinations")
                self.view.set_combination_cmb_items(combinations)
                self.combination_loaded.emit()
            else:
                self.api_manager.on_failure(reply)

        experiment_id = self.experiments.item_id(ex_index)
        self.api_manager.get_sensor_combinations(api_handler, experiment_id)

    def update_targets(self):
        ex_index = self.experiment_index

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                targets: Targets = self.targetsList[ex_index]
                targets.set_items_with_json(json_str, "targets")
                self.view.set_target_cmb_items(targets)
            else:
                self.api_manager.on_failure(reply)

        experiment_id = self.experiments.item_id(ex_index)
        self.api_manager.get_targets(api_handler, experiment_id)

    def on_data_changed(self):
        self.view.set_plate_name()

    def on_confirm_clicked(self):
        view: AddPlateView = self.view

        metal = self.metal_samples[self.metal_index]
        metal_made_at = metal.made_at
        metal_made_at_object = datetime.strptime(metal_made_at, "%Y-%m-%dT%H:%M:%S")

        date_str = view.wig_date.lb.text()
        hour_str = view.wig_hour.et.text()
        datetime_str = f"{date_str}_{hour_str}0000"
        datetime_object = datetime.strptime(datetime_str, "%y%m%d_%H%M%S")

        metal_age_object = datetime_object - metal_made_at_object
        metal_age = int(metal_age_object.total_seconds() / 3600)

        name = view.lb_plate_name.text()
        additive_samples = list(self.setting_manager.get_use_additive_samples())
        combination_id = self.combinationsList[self.experiment_index].item_id(self.combination_index)
        made_at = datetime_object.strftime('%Y-%m-%dT%H:%M:%S')

        common_data = {
                "name": name,
                "additive_samples": additive_samples,
                "sensor_combination": combination_id,
                "metal_sample": metal.id,
                "metal_age": metal_age,
                "made_at": made_at
            }

        if self.add_timeline:
            target_id = self.targetsList[self.experiment_index].item_id(self.target_index)
            body_name = "plate_timeline"
            common_data["target"] = target_id
            request = self.api_manager.add_timeline

        else:
            body_name = "plate"
            request = self.api_manager.add_plate

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                if self.add_timeline:
                    self.timeline_added_signal.emit(self)
                else:
                    self.plate_added_signal.emit(self)
            else:
                self.api_manager.on_failure(reply)

        request(api_handler, {body_name: common_data})


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AddPlateController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
