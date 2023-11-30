from PySide6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QPushButton


class HomeModel:
    def __init__(self):
        self.value = 0


class HomeView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller

    def set_controller(self, controller):
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.label = QLabel(str(self.controller.get_value()))
        self.btn_add = QPushButton("add")
        self.btn_sub = QPushButton("sub")

        layout = QVBoxLayout(self)

        layout.addWidget(self.label)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_sub)

        self.btn_add.clicked.connect(self.controller.add)
        self.btn_sub.clicked.connect(self.controller.sub)

    def update_label(self, value):
        self.label.setText(str(value))


class HomeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add(self):
        print("before add:", self.model.value)
        self.model.value += 1
        self.view.update_label(self.model.value)

    def sub(self):
        print("before sub:", self.model.value)
        self.model.value -= 1
        self.view.update_label(self.model.value)

    def get_value(self):
        return self.model.value


class MVC:
    def __init__(self, parent=None):
        # super().__init__(parent)

        self.model = HomeModel()
        self.view = HomeView(None, parent=parent)
        self.controller = HomeController(self.model, self.view)
        self.view.set_controller(self.controller)

    def get_view(self):
        return self.view


if __name__ == "__main__":
    app = QApplication([])

    # model = HomeModel()
    # view = HomeView(None)
    # controller = HomeController(model, view)
    #
    # view.set_controller(controller)
    # view.show()

    homePage = MVC()
    homePage.view.show()
    app.exec()
