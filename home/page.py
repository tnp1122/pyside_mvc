from home import *


class HomePage:
    def __init__(self, parent=None):
        self.model = HomeModel()
        self.view = HomeView(None, parent)
        self.controller = HomeController(self.model, self.view)
        self.view.set_controller(self.controller)

    def get_view(self):
        return self.view


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    page = HomePage()
    page.get_view().show()
    app.exec()
