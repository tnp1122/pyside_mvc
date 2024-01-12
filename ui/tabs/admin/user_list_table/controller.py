from ui.common.base_controller import BaseController
from ui.tabs.admin.user_list_table.model import UserListTableModel
from ui.tabs.admin.user_list_table.view import UserListTableView


class UserListTableWidget(BaseController):
    def __init__(self, parent=None):
        super().__init__(UserListTableModel, UserListTableView, parent)

        self.view.init_ui()

    def set_table_items(self, user_list):
        self.view.set_table_items(user_list)

    def clear_table_items(self):
        self.model.user_list = []
        self.view.clear_table()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = UserListTableWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
