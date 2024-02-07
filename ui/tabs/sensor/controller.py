from ui.common import BaseController
from ui.tabs.sensor import SensorModel, SensorView


class SensorController(BaseController):
    def __init__(self, parent=None):
        super().__init__(SensorModel, SensorView, parent)

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = SensorController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
