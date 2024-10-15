from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.mean_color import MeanColorModel, MeanColorView


class MeanColorController(BaseController):
    def __init__(self, parent=None):
        super().__init__(MeanColorModel, MeanColorView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MeanColorController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
