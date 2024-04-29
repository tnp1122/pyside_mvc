from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.mean_color import MeanColorModel, MeanColorView
from ui.tabs.experiment.window.snapshot.mean_color.image_list import ImageListController


class MeanColorController(BaseController):
    def __init__(self, parent=None):
        super().__init__(MeanColorModel, MeanColorView, parent)

    def init_controller(self):
        super().init_controller()

        view: MeanColorView = self.view
        view.radio.selected.connect(self.on_radio_selected)

    def on_radio_selected(self, index):
        image_list: ImageListController = self.view.image_list
        image_list.set_image_type(index)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MeanColorController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
