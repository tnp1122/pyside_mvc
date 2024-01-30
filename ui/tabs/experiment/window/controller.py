from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton

from ui.common import BaseController
from ui.tabs.experiment.window import ExperimentWindowModel, ExperimentWindowView


class ExperimentWindowController(BaseController):
    is_void_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(ExperimentWindowModel, ExperimentWindowView, parent)

    def init_controller(self):
        super().init_controller()

    def add_tab(self, widget, tab_name):
        self.view.addTab(self.view.with_container(widget), tab_name)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExperimentWindowController()

    btn = QPushButton("버튼")
    btn2 = QPushButton("버튼2")
    widget.add_tab(btn, "탭1")
    widget.add_tab(btn2, "탭2")
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
