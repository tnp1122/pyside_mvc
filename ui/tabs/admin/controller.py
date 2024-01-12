import json
import logging

from PySide6.QtNetwork import QNetworkReply

from data.api.api_manager import APIManager
from ui.common.base_controller import BaseController
from ui.tabs.admin import AdminModel
from ui.tabs.admin.view import AdminView

LOCATION = "[Admin Controller]"


class AdminWidget(BaseController):
    def __init__(self, parent=None):
        super().__init__(AdminModel, AdminView, parent)

        self.api_manager = APIManager()
        self.view.init_ui()

    def init_controller(self):
        self.view.btn_get_waiting_users.clicked.connect(self.get_user_list)
        self.view.table_waiting_users.view.approved_signal.connect(lambda index: self.on_approved(index))
        self.view.table_waiting_users.view.rejected_signal.connect(lambda index: self.on_rejected(index))

        self.get_user_list()

    def set_table_items(self, user_list):
        self.view.table_waiting_users.set_table_items(user_list)

    def get_user_list(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                user_list = json.loads(json_str)
                print(user_list)
                self.set_table_items(user_list)
            else:
                logging.error(f"{LOCATION} get_user_list-{reply.errorString()}")

        self.view.table_waiting_users.clear_table_items()
        self.api_manager.get_user_list(api_handler)

    def on_approved(self, index):
        print(f"승인: {index}")

    def on_rejected(self, index):
        print(f"거절: {index}")


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AdminWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
