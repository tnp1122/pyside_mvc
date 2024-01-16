from ui.common import BaseController
from ui.tabs.admin.user_list_table import UserListTableModel, UserListTableView


class UserListTableController(BaseController):
    def __init__(self, parent=None):
        super().__init__(UserListTableModel, UserListTableView, parent)

    def set_table_items(self, user_list):
        self.view.set_table_items(user_list)

    def clear_table_items(self):
        self.model.user_list = []
        self.view.clear_table()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = UserListTableController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
