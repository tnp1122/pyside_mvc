from ui.common import BaseController
from ui.tabs.experiment.plate.capture.mask_manager import MaskManagerView, MaskManagerModel
from util.enums import MaskViewIndex


class MaskManagerController(BaseController):
    def __init__(self, parent=None, origin_image=None):
        self.origin_image = origin_image

        super().__init__(MaskManagerModel, MaskManagerView, parent, origin_image)

    def init_text(self):
        self.view.ET_r.setText(str(self.graphics.model.circle_radius))

        self.view.ET_threshold.setText(str(self.view.masking.threshold))

    def init_controller(self):
        super().init_controller()

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
    from PySide6.QtWidgets import QApplication
    import os

    app = QApplication([])
    image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../plate_image.jpg")
    widget = MaskManagerController(origin_image=image_path)
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
