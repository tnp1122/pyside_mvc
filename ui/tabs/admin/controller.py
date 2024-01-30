import json
import logging

from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.common import BaseController
from ui.tabs.admin import AdminModel, AdminView

WIDGET = "[Admin Controller]"


class AdminController(BaseController):
    api_manager = APIManager()
    user_list = []

    def __init__(self, parent=None):
        super().__init__(AdminModel, AdminView, parent)

    def init_controller(self):
        super().init_controller()

        self.view.btn_get_waiting_users.clicked.connect(self.update_user_list)
        self.view.table_waiting_users.view.approved_signal.connect(lambda index: self.approve_handler(index, True))
        self.view.table_waiting_users.view.rejected_signal.connect(lambda index: self.approve_handler(index, False))

        self.update_user_list()

    def set_table_items(self, user_list):
        self.view.table_waiting_users.set_table_items(user_list)

    def update_user_list(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.user_list = json.loads(json_str)["user_list"]
                self.set_table_items(self.user_list)
            else:
                logging.error(f"{WIDGET} get_user_list-{reply.errorString()}")

        self.view.table_waiting_users.clear_table_items()
        self.api_manager.get_user_list(api_handler)

    def approve_handler(self, index, approved):

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                self.update_user_list()
            else:
                logging.error(f"{WIDGET} approve_handler: {reply.errorString()}")

        result = {"approve": approved}
        self.api_manager.approve_user(api_handler, result, self.user_list[index]["id"])


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AdminController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
