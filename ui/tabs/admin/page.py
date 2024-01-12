from ui.tabs.admin import *


class AdminPage:
    def __init__(self, parent=None):
        print("adminPage: init")
        self.model = AdminModel()
        self.view = AdminView(None, parent)
        self.controller = AdminController(self.model, self.view)
        self.view.set_controller(self.controller)

    def get_view(self):
        return self.view

    def set_table_items(self, user_list):
        self.controller.set_table_items(user_list)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    page = AdminPage()
    page.get_view().show()
    app.exec()
