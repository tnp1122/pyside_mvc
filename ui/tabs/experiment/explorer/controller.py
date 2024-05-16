import json
from collections import OrderedDict

from PySide6.QtNetwork import QNetworkReply

from ui.common import BaseController
from ui.tabs.experiment.explorer import ExplorerModel, ExplorerView
from util.convert import convert_to_ordered_dict


class ExplorerController(BaseController):
    experiment_tree = OrderedDict()
    transformed_tree = OrderedDict()

    def __init__(self, parent=None):
        super().__init__(ExplorerModel, ExplorerView, parent)

    def init_controller(self):
        super().init_controller()

        self.view.btn_refresh.clicked.connect(self.update_tree_view)
        self.update_tree_view()

    def update_tree_view(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                experiment_tree = json.loads(json_str)["experiment_tree"]
                self.experiment_tree = convert_to_ordered_dict(experiment_tree)
                self.transformed_tree = self.transform_to_tree_view_form(self.experiment_tree)
                self.view.set_tree_items(self.transformed_tree)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.get_experiment_tree(api_handler)

    def transform_to_tree_view_form(self, experiment_tree):
        experiment_branch = OrderedDict()
        for experiment in experiment_tree:
            experiment_name = experiment["name"]
            combinations = experiment["sensor_combinations"]
            combination_branch = OrderedDict()
            for combination in combinations:
                combination_name = combination["name"]
                plates = combination["plates"]
                plate_branch = OrderedDict()

                timelines = combination.get("timelines")
                if timelines:
                    timeline_branch = []
                    for timeline in timelines:
                        timeline_name = timeline["name"]
                        timeline_branch.append(timeline_name)
                    if timeline_branch:
                        plate_branch["연속촬영"] = timeline_branch

                for plate in plates:
                    plate_name = plate["name"]
                    snapshots = plate["plate_snapshots"]
                    snapshot_branch = []
                    for snapshot in snapshots:
                        snapshot_name = str(snapshot["age"]) + "H"
                        snapshot_branch.append(snapshot_name)
                    plate_branch[plate_name] = snapshot_branch
                combination_branch[combination_name] = plate_branch
            experiment_branch[experiment_name] = combination_branch
        return experiment_branch


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExplorerController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
