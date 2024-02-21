from PySide6.QtWidgets import QPushButton, QWidget

from ui.common import BaseController
from ui.tabs.experiment.window import ExperimentWindowModel, ExperimentWindowView


class ExperimentWindowController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ExperimentWindowModel, ExperimentWindowView, parent)

    def init_controller(self):
        super().init_controller()

    def add_tab(self, widget, tab_name):
        self.view.addTab(self.view.with_container(widget, mode=1), tab_name)

    def get_index(self, widget):
        for i in range(self.view.count()):
            container = self.view.widget(i)
            if container.findChild(QWidget, widget.objectName()) == widget:
                return i
        return -1

    def remove_tab(self, widget):
        index = self.get_index(widget)
        self.view.removeTab(index)

    def remove_tab_with_index(self, index):
        self.view.removeTab(index)


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
