from admin.user_list_table import *


class UserListTable:
    def __init__(self, parent=None):
        self.model = UserListTableModel()
        self.view = UserListTableView(None, parent)
        self.controller = UserListTableController(self.model, self.view)
        self.view.set_controller(self.controller)

    def get_view(self):
        return self.view

    def set_table_items(self, user_list):
        self.controller.set_table_items(user_list)

    def clear_table_items(self):
        self.controller.clear_table_items()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    table = UserListTable()
    table.get_view().show()
    app.exec()
