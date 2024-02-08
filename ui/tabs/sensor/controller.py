from ui.common import TabWidgetController
from ui.tabs.sensor import SensorModel, SensorView


class SensorController(TabWidgetController):
    initialized_tabs = []
    tab_count = 0

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
