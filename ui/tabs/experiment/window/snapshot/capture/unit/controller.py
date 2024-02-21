from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.capture.unit import PlateCaptureUnitModel, PlateCaptureUnitView


class PlateCaptureUnitController(BaseController):
    def __init__(self, parent=None):
        super().__init__(PlateCaptureUnitModel, PlateCaptureUnitView, parent)

    def init_controller(self):
        super().init_controller()

    def set_image_size(self, width=None, height=None):
        self.view.set_image_size(width, height)

    def set_selected(self, is_selected):
        self.view.set_selected(is_selected)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = PlateCaptureUnitController()
    widget.view.set_image_size(300, 500)
    widget.view.set_no_image()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
