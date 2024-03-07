from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListController
from ui.tabs.experiment.window.snapshot.process.unit import PlateCaptureUnitController, PlateCaptureUnitView
from ui.tabs.experiment.window.snapshot.extract import ColorExtractModel, ColorExtractView


class ColorExtractController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ColorExtractModel, ColorExtractView, parent)

    def init_controller(self):
        super().init_controller()

        view: ColorExtractView = self.view
        view.radio.selected.connect(self.on_radio_selected)

    def set_image_list(self, capture_list: CaptureListController):
        view: ColorExtractView = self.view
        view.image_list.clear()

        capture_units = capture_list.view.units
        for unit in capture_units:
            unit: PlateCaptureUnitController
            unit_view: PlateCaptureUnitView = unit.view

            mean_colored_pixmap = unit.mean_colored_pixmap
            cropped_original_pixmap = unit.cropped_original_pixmap
            target_name = unit_view.cmb_target.currentText()

            if unit.mean_colors:
                view.image_list.add_new_image(mean_colored_pixmap, cropped_original_pixmap, target_name)

    def on_radio_selected(self, index):
        view: ColorExtractView = self.view
        view.image_list.set_image_index(index)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ColorExtractController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
