from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from ui.experiment.plate.capture.mask_manager import MaskManagerView, MaskViewIndex, MaskManagerModel


class MaskManagerWidget:
    def __init__(self, origin_image, parent=None):
        self._model = MaskManagerModel()
        self._view = MaskManagerView(origin_image, parent)

        self.view.ui_initialized_signal.connect(self.connect_button_signal)
        self.view.init_ui()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def connect_button_signal(self):
        self.view.view_radio.selected.connect(self.on_select_changed)
        self.view.btn_set_horizontal.clicked.connect(lambda: self.view.graphics.set_direction(0))
        self.view.btn_set_vertical.clicked.connect(lambda: self.view.graphics.set_direction(1))
        self.view.btn_circle.clicked.connect(self.set_circle_visible)

    def on_select_changed(self, index):
        view_index = MaskViewIndex(index)
        self.model.current_view = view_index
        self.view.graphics.view_handler.set_current_view(view_index)

    def set_circle_visible(self):
        self.view.graphics.set_circle_visible(not self.view.graphics.is_circle_visible())


def main():
    app = QApplication([])
    image = QImage("../plate_image.jpg")
    widget = MaskManagerWidget(image)
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
