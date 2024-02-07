from ui.tabs.sensor.tabs.base_tab import SensorBaseTabController
from ui.tabs.sensor.tabs.tables.metal_sample_table import MetalSampleTableController
from ui.tabs.sensor.tabs.tables.metal_table import MetalTableController


class MetalTabController(SensorBaseTabController):
    def __init__(self, parent=None):
        subject_name = "metal"
        super().__init__(parent, subject_name)


    def init_view(self):
        self.view.sample = MetalSampleTableController()
        self.view.subject = MetalTableController()

        super().init_view()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MetalTabController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
