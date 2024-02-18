import json

from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.common import BaseController
from ui.common.toast import Toast
from ui.tabs.combination import CombinationModel, CombinationView
from ui.tabs.combination.widgets import BaseCell, Cell

WIDGET = "[Combination Controller]"


class CombinationController(BaseController):
    api_manager = APIManager()

    experiments = []
    combinations = []
    experiment_index = -1
    combination_index = -1

    solvents = []
    additives = []

    is_editable = False

    def __init__(self, parent=None):
        super().__init__(CombinationModel, CombinationView, parent)

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()

        view: CombinationView = self.view

        view.btn_refresh.clicked.connect(self.refresh)
        view.btn_cancel.clicked.connect(self.on_cancel_clicked)
        view.btn_save.clicked.connect(self.on_save_clicked)
        view.btn_new_combination.clicked.connect(self.on_new_combination_clicked)

        view.cmb_experiment.currentIndexChanged.connect(self.on_experiment_changed)
        view.cmb_combination.currentIndexChanged.connect(self.on_combination_changed)

        view.cell_clicked_signal.connect(lambda index: self.on_cell_clicked(index))

        view.select_sensor_widget.btn_refresh.clicked.connect(self.refresh_material)
        view.select_sensor_widget.btn_confirm.clicked.connect(self.on_sensor_confirm_clicked)

        self.set_editable(False)
        self.refresh()
        self.refresh_material()

    def refresh(self):
        self.experiments = []
        self.combinations = []
        self.experiment_index = -1
        self.combination_index = -1
        self.update_experiments()

    def refresh_material(self):
        self.update_solvents()
        self.update_additives()

    def set_editable(self, editable: bool):
        self.is_editable = editable
        view: CombinationView = self.view
        if editable:
            view.cmb_combination.setVisible(False)
            view.btn_refresh.setVisible(False)
            view.btn_new_combination.setVisible(False)

            view.et_combination_name.setVisible(True)
            view.btn_cancel.setVisible(True)
            view.btn_save.setVisible(True)

        else:
            view.cmb_combination.setVisible(True)
            view.btn_refresh.setVisible(True)
            view.btn_new_combination.setVisible(True)

            view.et_combination_name.setVisible(False)
            view.btn_cancel.setVisible(False)
            view.btn_save.setVisible(False)

        view.switch_cell_style(editable)

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

    def update_combinations(self):
        ex_index = self.experiment_index

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                combination = json.loads(json_str)["sensor_combinations"]
                self.combinations[ex_index] = combination
                self.view.set_combination_cmb_items(self.combinations[ex_index])
                self.load_sensors()
            else:
                self.api_manager.on_failure(reply)

        experiment_id = self.experiments[ex_index]["id"]
        self.api_manager.get_sensor_combination(api_handler, experiment_id)

    def update_solvents(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.solvents = json.loads(json_str)["solvents"]
                self.view.select_sensor_widget.set_cmb_solvent(self.solvents)
            else:
                self.api_manager.on_failure(reply)

        self.view.select_sensor_widget.set_cmb_solvent([])
        self.api_manager.get_solvents(api_handler)

    def update_additives(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.additives = json.loads(json_str)["additives"]
                self.view.select_sensor_widget.set_cmb_additive(self.additives)
            else:
                self.api_manager.on_failure(reply)

        self.view.select_sensor_widget.set_cmb_additive([])
        self.api_manager.get_additives(api_handler)

    def on_cancel_clicked(self):
        self.set_editable(False)
        self.load_sensors()

    def on_save_clicked(self):
        view: CombinationView = self.view

        name = view.et_combination_name.text()
        combination = {"name": name, "sensor_associations": []}

        ex_index = self.experiment_index
        ex_id = self.experiments[ex_index]["id"]

        for y in range(11, -1, -1):
            for x in range(1, 9):
                cell: Cell = view.lyt_grid.itemAtPosition(y, x).widget()
                solvent_id = cell.solvent["id"]
                additive_id = cell.additive["id"]
                if solvent_id == -1 or additive_id == -1:
                    continue
                associataion = {"sensor": {"solvent": solvent_id, "additive": additive_id}, "idx": cell.index}
                combination["sensor_associations"].append(associataion)

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                combination_response = json.loads(json_str)["sensor_combination"]
                self.combinations[ex_index].append(combination_response)
                self.set_editable(False)

                last_index = len(self.combinations[ex_index]) - 1
                view.set_combination_cmb_items(self.combinations[ex_index])
                view.cmb_combination.setCurrentIndex(last_index)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.add_sensor_combination(api_handler, ex_id, combination)

    def on_new_combination_clicked(self):
        if not self.experiments:
            Toast().toast("실험을 생성하세요.")
            return

        if self.combinations[self.experiment_index]:
            combination_name = self.combinations[self.experiment_index][self.combination_index]["name"] + " (2)"
        else:
            combination_name = "새 조합"
        self.view.et_combination_name.setText(combination_name)
        self.set_editable(True)

    def load_sensors(self):
        ex_index = self.experiment_index
        cm_index = self.combination_index
        if self.combinations[ex_index]:
            associations = self.combinations[ex_index][cm_index]["sensor_associations"]
        else:
            associations = []
        self.view.set_grid_items(associations)

    def on_experiment_changed(self, event):
        if event > -1:
            if self.experiments:
                self.experiment_index = event
                if not self.is_editable:
                    if len(self.combinations) > event and self.combinations[event]:
                        self.view.set_combination_cmb_items(self.combinations[self.experiment_index])

                        self.load_sensors()
                    else:
                        self.update_combinations()

    def on_combination_changed(self, event):
        if event > -1:
            self.combination_index = event
            self.load_sensors()

    def on_cell_clicked(self, index: str):
        view: CombinationView = self.view
        if self.is_editable:
            x, y = [int(value) for value in index.split(", ")]
            cell: BaseCell = view.lyt_grid.itemAtPosition(y, x).widget()

            def get_index(cell_item, items):
                if cell_item["name"]:
                    for i, item in enumerate(items):
                        if item["name"] == cell_item["name"]:
                            return i + 1
                return 0

            solvent_index = get_index(cell.solvent, self.solvents)
            additive_index = get_index(cell.additive, self.additives)
            view.select_sensor_widget.set_selected_index(solvent_index, additive_index)

            if x == 0:
                view.select_sensor_widget.set_solvent_invisible()
            elif y == 12:
                view.select_sensor_widget.set_additive_invisible()

            view.select_sensor_widget.custom_exec(x, y)

    def on_sensor_confirm_clicked(self):
        view: CombinationView = self.view
        x_index, y_index = view.select_sensor_widget.x, view.select_sensor_widget.y
        solvent_index, additive_index = view.select_sensor_widget.get_selected_index()
        view.select_sensor_widget.close()

        cell: BaseCell = view.lyt_grid.itemAtPosition(y_index, x_index).widget()

        solvent = None if solvent_index == 0 else self.solvents[solvent_index - 1]
        additive = None if additive_index == 0 else self.additives[additive_index - 1]

        cell.set_solvent(solvent)
        cell.set_additive(additive)
        if x_index == 0:
            for x in range(1, 9):
                cell: BaseCell = view.lyt_grid.itemAtPosition(y_index, x).widget()
                cell.set_solvent(solvent)
        elif y_index == 12:
            for y in range(12):
                cell: BaseCell = view.lyt_grid.itemAtPosition(y, x_index).widget()
                cell.set_additive(additive)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = CombinationController()
    widget.late_init()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
