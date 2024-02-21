from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.capture import PlateCaptureModel, PlateCaptureView


class PlateCaptureController(BaseController):
    def __init__(self, parent=None):
        super().__init__(PlateCaptureModel, PlateCaptureView, parent)

    def init_controller(self):
        pass

    def late_init(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = PlateCaptureController()
    widget.late_init()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
