from ui.tabs.material.tabs.base_tab import SensorBaseTabController
from ui.tabs.material.tabs.tables.solvent_table import SolventTableController


class SolventTabController(SensorBaseTabController):
    def __init__(self, parent=None):
        subject_name = "solvent"
        super().__init__(parent, subject_name)

    def init_view(self):
        self.view.subject = SolventTableController()
        
        super().init_view()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = SolventTabController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
