import json

from data.api.api_manager import APIManager


class AdminController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.ui_initialized_signal.connect(self.get_user_list)
        self.api_manager = APIManager()

    def set_table_items(self, user_list):
        self.view.table.set_table_items(user_list)

    def get_user_list(self):
        print("adminController: get_user_list")

        def api_handler(reply):
            json_str = reply.readAll().data().decode("utf-8")
            user_list = json.loads(json_str)
            print(user_list)
            self.set_table_items(user_list)

        self.view.table.clear_table_items()
        self.api_manager.get_user_list(api_handler)
