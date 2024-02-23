import sys

import numpy as np
from numpy import ndarray

from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.capture.unit import PlateCaptureUnitModel, PlateCaptureUnitView


class PlateCaptureUnitController(BaseController):
    def __init__(self, parent=None):
        super().__init__(PlateCaptureUnitModel, PlateCaptureUnitView, parent)

        self.masked_array: ndarray
        self.mask_info = {}

        view: PlateCaptureUnitView = self.view
        view.mask_manager_apply_clicked.connect(self.on_mask_apply_clicked)

    def close(self):
        self.masked_array = None
        self.mask_info = None

        super().close()

    def init_controller(self):
        super().init_controller()

    def set_image_size(self, width=None, height=None):
        self.view.set_image_size(width, height)

    def set_selected(self, is_selected):
        self.view.set_selected(is_selected)

    def on_mask_apply_clicked(self):
        self.masked_array = self.view.mask_manager.view.masking.masked_array
        self.mask_info = self.view.mask_manager.view.graphics.get_circle_mask_info()
        x = self.mask_info["x"]
        y = self.mask_info["y"]
        if self.mask_info["direction"] == 0:
            width = self.mask_info["width"]
            height = self.mask_info['height']
        else:
            width = self.mask_info['height']
            height = self.mask_info["width"]

        self.view.set_cropped_image(x, y, width, height)
        np.savez_compressed('compressed_data.npz', self.masked_array.mask)

        self.view.mask_manager.close()



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
