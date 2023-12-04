from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QHBoxLayout

from admin import AdminPage
from mvc2 import MVC
from home import HomePage


class MainWindowModel:
    def __init__(self):
        pass


class MainWindowView(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

    def set_controller(self, controller):
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # self.stacked_widget = QStackedWidget(self)
        widget = QWidget(self)
        self.setCentralWidget(widget)
        lyt = QHBoxLayout(widget)

        home = HomePage()
        admin = AdminPage()

        lyt.addWidget(home.get_view())
        lyt.addWidget(admin.get_view())


class MainWindowController:
    def __init__(self, model, view):
        self.model = model
        self.view = view


class PitApp:
    def __init__(self):
        self.app = QApplication([])

        self.model = MainWindowModel
        self.view = MainWindowView(None)
        self.controller = MainWindowController(self.model, self.view)
        self.view.set_controller(self.controller)
        self.view.show()

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    app = PitApp()
    exit_code = app.run()
    exit(exit_code)
