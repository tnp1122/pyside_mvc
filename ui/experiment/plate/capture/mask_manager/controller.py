from PySide6.QtWidgets import QApplication

from ui.experiment.plate.capture.mask_manager import MaskManagerView, MaskViewIndex, MaskManagerModel


class MaskManagerWidget:
    def __init__(self, origin_image, parent=None):
        self._model = MaskManagerModel()
        self._view = MaskManagerView(origin_image, parent)
        self.graphics = None

        self.view.ui_initialized_signal.connect(self.init_controller)
        self.view.init_ui()
        self.init_text()
        self.update_masking_view()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def init_text(self):
        self.view.ET_r.setText(str(self.graphics.model.circle_radius))

        self.view.ET_threshold.setText(str(self.view.masking.threshold))

    def init_controller(self):
        self.graphics = self.view.graphics
        self.view.view_radio.selected.connect(self.on_select_changed)
        self.view.btn_set_horizontal.clicked.connect(lambda: self.graphics.set_direction(0))
        self.view.btn_set_vertical.clicked.connect(lambda: self.graphics.set_direction(1))
        self.view.btn_circle.clicked.connect(self.set_circle_visible)

        self.view.btn_show_masking.clicked.connect(self.show_masking_view)
        self.view.ET_r.textChanged.connect(self.on_change_radius)

        self.view.ET_threshold.textChanged.connect(self.on_change_threshold)

        self.view.masking.masked_image_updated_signal.connect(self.update_masking_view)

    def on_select_changed(self, index):
        view_index = MaskViewIndex(index)
        self.model.current_view = view_index
        self.graphics.view_handler.set_current_view(view_index)
        self.view.set_bottom_lyt(index)

        if view_index == MaskViewIndex.DISTRICT:
            self.graphics.model.is_border_adjustable = True
        else:
            self.graphics.model.is_border_adjustable = False

        if view_index == MaskViewIndex.MASK:
            circle_mask_info = self.graphics.model.get_circle_mask_info()
            self.view.masking.set_circle_mask(circle_mask_info)

    def set_circle_visible(self):
        self.graphics.set_circle_visible(not self.graphics.is_circle_visible())

    def update_masking_view(self):
        self.graphics.set_masking_view(self.view.masking.get_pixmap())

    def show_masking_view(self):
        self.view.masking.show_image()

    def on_change_radius(self, radius):
        if radius == "":
            return
        self.graphics.set_circle_radius(int(radius))

    def on_change_threshold(self, threshold):
        if threshold == "" or not (0 < int(threshold) < 255):
            return
        self.view.masking.set_threshold(int(threshold))


def main():
    app = QApplication([])
    image_path = "../plate_image.jpg"
    widget = MaskManagerWidget(image_path)
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
