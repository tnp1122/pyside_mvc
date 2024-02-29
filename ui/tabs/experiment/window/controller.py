from PySide6.QtWidgets import QPushButton, QWidget

from ui.common import BaseController
from ui.tabs.experiment.window import ExperimentWindowModel, ExperimentWindowView
from ui.tabs.experiment.window.snapshot.capture import PlateCaptureView


class ExperimentWindowController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ExperimentWindowModel, ExperimentWindowView, parent)

    def init_controller(self):
        super().init_controller()

    def get_index(self, widget):
        for i in range(self.view.count()):
            container = self.view.widget(i)
            if container.findChild(QWidget, widget.objectName()) == widget:
                return i
        return -1

    def add_tab(self, controller: BaseController, mode, tab_name):
        view: ExperimentWindowView = self.view

        view.addTab(view.with_container(controller.view, mode=mode), tab_name)
        capture_view: PlateCaptureView = controller.view.plate_capture.view
        capture_view.set_tab_name.connect(lambda name: self.set_tab_name(controller, name))

    def remove_tab(self, controller: BaseController):
        index = self.get_index(controller.view)
        self.view.removeTab(index)
        controller.close()

    def set_tab_name(self, controller, name):
        view: ExperimentWindowView = self.view
        index = self.get_index(controller.view)
        view.setTabText(index, name)


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
