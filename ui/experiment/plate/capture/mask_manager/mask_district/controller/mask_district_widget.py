from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow

from ui.experiment.plate.capture.mask_manager.mask_district import MaskDistrictModel, MaskDistrictView
from ui.experiment.plate.capture.mask_manager.mask_district.controller.mouse_handler import MouseHandler


class MaskDistrictWidget(MouseHandler):
    def __init__(self, origin_image, parent=None):
        self._model = MaskDistrictModel()
        self._view = MaskDistrictView(origin_image, parent)

        self.add_border()
        self.add_mask_area()
        self.add_axes()

        super().__init__(self.model, self.view)
        self.view.set_scene()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def add_border(self):
        x = self.model.area_x
        y = self.model.area_y
        width = self.model.area_width
        height = self.model.area_height
        border_width = self.model.border_width
        margin = self.model.axis_head_height
        self.view.scene.add_border(x, y, width, height, border_width, margin)

    def add_mask_area(self):
        border = self.view.scene.border
        model = self.model
        border.add_mask_area(model.area_x, model.area_y, model.area_width, model.area_height, model.border_width)

    def add_axes(self):
        border = self.view.scene.border

        ver_bar_start = self.model.area_y
        hor_bar_start = self.model.area_x
        ver_bar_height = self.model.area_height
        hor_bar_height = self.model.area_width

        head_width = 20
        head_height = self.model.axis_head_height
        bar_width = 10

        for value in self.model.additive_axes:
            x_pos = self.model.area_x + value
            border.add_axes(value=x_pos, bar_start=ver_bar_start, head_width=head_width, head_height=head_height,
                            bar_width=bar_width, bar_height=ver_bar_height, is_vertical=True)

        for value in self.model.solvent_axes:
            y_pos = self.model.area_y + value
            border.add_axes(value=y_pos, bar_start=hor_bar_start, head_width=head_width, head_height=head_height,
                            bar_width=bar_width, bar_height=hor_bar_height)

    def set_direction(self, direction):
        if not (direction == 0 or direction == 1):
            raise ValueError("방향은 0 또는 1이여야 합니다.")

        self.model.direction = direction
        angle = self.model.direction * (- 90) + self.model.rotation
        self.border.setRotation(angle)


def main():
    app = QApplication([])
    widget = QWidget()
    image = QImage("../../../plate_image.jpg")
    district = MaskDistrictWidget(image)
    btn_horizontal = QPushButton("가로")
    btn_vertical = QPushButton("세로")
    btn_horizontal.clicked.connect(lambda: district.set_direction(0))
    btn_vertical.clicked.connect(lambda: district.set_direction(1))

    lyt = QVBoxLayout(widget)
    lyt.addWidget(district.view)
    lyt.addWidget(btn_horizontal)
    lyt.addWidget(btn_vertical)

    widget.show()

    app.exec()


if __name__ == "__main__":
    main()
