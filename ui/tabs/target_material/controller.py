import logging

from PySide6.QtNetwork import QNetworkReply

from model import Experiments, Targets
from ui.common import BaseController
from ui.common.toast import Toast
from ui.tabs.target_material import TargetMaterialModel, TargetMaterialView

WIDGET = "[Target Material Controller]"


class TargetMaterialController(BaseController):

    def __init__(self, parent=None):
        super().__init__(TargetMaterialModel, TargetMaterialView, parent)

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()
        self.experiments = Experiments()
        self.targets = Targets()

        view: TargetMaterialView = self.view

        view.cmb.currentIndexChanged.connect(self.update_targets)

        view.btn_refresh.clicked.connect(self.update_experiments)
        view.btn_cancle.clicked.connect(view.tb_target.cancel_added_items)
        view.btn_save.clicked.connect(self.save_new_targets)

        self.update_experiments()

    def update_experiments(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.experiments.set_items_with_json(json_str, "experiments")
                self.view.set_experiment_cmb_items(self.experiments)
            else:
                msg = f"{WIDGET} update_experiments-{reply.errorString()}"
                logging.error(msg)
                Toast().toast(msg)

        self.api_manager.get_experiments(api_handler)

    def update_targets(self, index):
        experiment_id = self.experiments.item_id(index)
        self.view.tb_target.view.update_experiment_id(experiment_id)

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.targets.set_items_with_json(json_str, "targets")
                self.view.set_target_table_items(self.targets)
            else:
                msg = f"{WIDGET} update_targets-{reply.errorString()}"
                logging.error(msg)
                Toast().toast(msg)

        self.api_manager.get_targets(api_handler, experiment_id)

    def save_new_targets(self):
        new_targets = [s.strip() for s in self.view.tb_target.get_new_items() if s.strip()]
        body = {"targets": [{"name": target} for target in new_targets]}

        if not body["targets"]:
            return

        index = self.view.cmb.currentIndex()
        experiment_id = self.experiments.item_id(index)

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                self.update_targets(index)
            else:
                self.api_manager.on_failure(reply)

        self.api_manager.add_targets(api_handler, experiment_id, body)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = TargetMaterialController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
