from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from ui.experiment.plate.capture.mask_manager import MaskManagerView, MaskViewIndex, MaskManagerModel


class MaskManagerWidget:
    def __init__(self, origin_image, parent=None):
        self.model = MaskManagerModel()
        self._view = MaskManagerView(origin_image, parent)
        self.connect_button_signal()

    @property
    def view(self):
        return self._view

    def connect_button_signal(self):
        self.view.btn_mask_district.clicked.connect(self.on_btn_mask_district_clicked)
        self.view.btn_mask_area.clicked.connect(self.on_btn_mask_area_clicked)

    def on_btn_mask_district_clicked(self):
        if self.view.btn_mask_district.isChecked():
            self.model.current_view = MaskViewIndex.DISTRICT
            if self.view.btn_mask_area.isChecked():
                self.view.btn_mask_area.setChecked(False)

        else:
            self.model.current_view = MaskViewIndex.ORIGIN

    def on_btn_mask_area_clicked(self):
        if self.view.btn_mask_district.isChecked():
            self.model.current_view = MaskViewIndex.MASK
            if self.view.btn_mask_district.isChecked():
                self.view.btn_mask_district.setChecked(False)

        else:
            self.model.current_view = MaskViewIndex.ORIGIN


def main():
    app = QApplication([])
    image = QImage("../plate_image.jpg")
    widget = MaskManagerWidget(image)
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
