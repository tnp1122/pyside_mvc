from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton

from ui.admin import AdminPage
from ui.home import HomePage
from ui.experiment.plate.capture.mask_manager.mask_district.controller.mask_district_widget import MaskDistrictWidget


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
        image = QImage("ui/experiment/plate/capture/plate_image.jpg")
        district = MaskDistrictWidget(image)
        district.set_direction(0)
        btn_horizontal = QPushButton("가로")
        btn_vertical = QPushButton("세로")
        btn_horizontal.clicked.connect(lambda: district.set_direction(0))
        btn_vertical.clicked.connect(lambda: district.set_direction(1))

        lyt.addWidget(home.get_view())
        lyt.addWidget(admin.get_view())
        lyt.addWidget(district.view)
        lyt.addWidget(btn_horizontal)
        lyt.addWidget(btn_vertical)


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
