from ui.tabs.material.tabs.base_tab import SensorBaseTabController
from ui.tabs.material.tabs.tables.additive_sample_table import AdditiveSampleTableController
from ui.tabs.material.tabs.tables.additive_table import AdditiveTableController


class AdditiveTabController(SensorBaseTabController):
    def __init__(self, parent=None):
        subject_name = "additive"
        super().__init__(parent, subject_name)

    def init_view(self):
        self.view.sample = AdditiveSampleTableController()
        self.view.subject = AdditiveTableController()

        super().init_view()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AdditiveTabController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
