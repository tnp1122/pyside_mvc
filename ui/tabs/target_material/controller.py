import json
import logging

from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.common import BaseController
from ui.common.toast import Toast
from ui.tabs.target_material import TargetMaterialModel, TargetMaterialView

WIDGET = "[Target Material Controller]"


class TargetMaterialController(BaseController):
    api_manager = APIManager()
    experiment_list = []
    target_list = []

    def __init__(self, parent=None):
        super().__init__(TargetMaterialModel, TargetMaterialView, parent)

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()

        self.view.cb.currentIndexChanged.connect(self.update_target_list)

        self.view.btn_refresh.clicked.connect(self.update_experiment_list)
        self.view.btn_cancle.clicked.connect(self.view.target_list_table.cancel_added_items)
        self.view.btn_save.clicked.connect(self.save_new_target_list)

        self.update_experiment_list()

    def save_new_target_list(self):
        new_targets = [s.strip() for s in self.view.target_list_table.get_new_list() if s.strip()]
        print(f"added row: {self.view.target_list_table.get_new_list()}")
        print(f"new targets: {new_targets}")
        body = {}
        body["targets"] = [{"name": target} for target in new_targets]
        index = self.view.cb.currentIndex()
        experiment_id = self.experiment_list[index]["id"]

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                print(f"add success")
                self.update_target_list(index)
            else:
                msg = f"{WIDGET} save_new_target_list-{reply.errorString()}"
                logging.error(msg)
                Toast().toast(msg)

        self.api_manager.add_targets(api_handler, experiment_id, body)

    def update_experiment_list(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.experiment_list = json.loads(json_str)["experiments"]
                self.view.set_combo_box_items(self.experiment_list)
            else:
                msg = f"{WIDGET} update_experiment_list-{reply.errorString()}"
                logging.error(msg)
                Toast().toast(msg)

        self.api_manager.get_experiment_list(api_handler)

    def update_target_list(self, index):
        experiment_id = self.experiment_list[index]["id"]
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                print(f"update_target_list")
                json_str = reply.readAll().data().decode("utf-8")
                self.target_list = json.loads(json_str)["targets"]
                self.view.set_target_list_table_items(self.target_list)
            else:
                msg = f"{WIDGET} update_target_list-{reply.errorString()}"
                logging.error(msg)
                Toast().toast(msg)

        self.api_manager.get_target_list(api_handler, experiment_id)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = TargetMaterialController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
