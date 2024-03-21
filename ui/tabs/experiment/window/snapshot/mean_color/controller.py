from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.mean_color import MeanColorModel, MeanColorView
from ui.tabs.experiment.window.snapshot.mean_color.image_list import ImageListView


class MeanColorController(BaseController):
    def __init__(self, parent=None):
        super().__init__(MeanColorModel, MeanColorView, parent)

    def init_controller(self):
        super().init_controller()

        view: MeanColorView = self.view
        view.radio.selected.connect(self.on_radio_selected)

    def add_image_shell(self):
        image_list_view: ImageListView = self.view.image_list.view
        image_list_view.add_image_shell()

    def set_image_shell(self, index, mean_colored_pixmap, cropped_original_pixmap, target_name):
        image_list_view: ImageListView = self.view.image_list.view
        image_list_view.set_image_shell(index, mean_colored_pixmap, cropped_original_pixmap, target_name)

    def on_radio_selected(self, index):
        view: MeanColorView = self.view
        view.image_list.set_image_type(index)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MeanColorController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
