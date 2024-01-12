from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

from ui.tabs.experiment.plate.capture.mask_manager.mask_graphics import MaskGraphicsModel, MaskGraphicsView
from ui.tabs.experiment.plate.capture.mask_manager.mask_graphics.controller.mouse_handler import MouseHandler
from ui.tabs.experiment.plate.capture.mask_manager.mask_graphics.controller.view_handler import ViewHandler


class MaskGraphicsWidget(MouseHandler):
    def __init__(self, origin_image, parent=None):
        self._model = MaskGraphicsModel()
        self._view = MaskGraphicsView(parent)
        self.view.set_scene(origin_image)
        self.add_border()

        super().__init__(self.model, self.view)
        self.view_handler = ViewHandler(self.model, self.view)
        self.set_border()

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

        self.view.scene.add_border(x, y, width, height, border_width)

    def set_border(self):
        self.set_direction(self.model.direction)
        self.set_circle_visible(self.model.is_circle_visible)
        self.set_circle_radius(self.model.circle_radius)

    def set_position(self, x=None, y=None, width=None, height=None):

        if x is not None:
            self.model.area_x = x
            self.border.setRect

    def is_circle_visible(self):
        return self.model.is_circle_visible

    def set_circle_visible(self, is_visible):
        self.model.is_circle_visible = is_visible
        self.border.set_circle_visible(is_visible)

    def set_direction(self, direction):
        if not (direction == 0 or direction == 1):  # 0: 가로, 1: 세로
            raise ValueError("방향이 올바르지 않습니다.")

        self.model.direction = direction
        self.border.set_direction(direction)

        if direction == 0:
            width = self.model.area_width
            height = self.model.area_height
        else:
            width = self.model.area_height
            height = self.model.area_width

        scened_x, scened_y = self.model.scened_x, self.model.scened_y
        self.border.setRect(scened_x, scened_y, width, height)
        self.border.mask_area.setRect(scened_x, scened_y, width, height)
        self.init_intervals()
        self.set_circles_center()

    def init_intervals(self):
        scened_x, scened_y = self.model.scened_x, self.model.scened_y
        if self.model.direction == 0:
            vertical_axes = [scened_x + axis for axis in self.model.additive_axes]
            horizontal_axes = [scened_y + axis for axis in self.model.solvent_axes]
            width = self.model.area_width
            height = self.model.area_height
        else:
            vertical_axes = [scened_x + axis for axis in self.model.solvent_axes]
            horizontal_axes = [scened_y + axis for axis in self.model.additive_axes]
            width = self.model.area_height
            height = self.model.area_width

        self.border.set_intervals(vertical_axes, is_up_down_interval=False)
        self.border.set_intervals(horizontal_axes, is_up_down_interval=True)
        self.border.set_bar_height(height, 0, is_vertical=True)
        self.border.set_bar_height(width, 0, is_vertical=False)

    def set_circles_center(self):
        scened_x, scened_y = self.model.scened_x, self.model.scened_y
        if self.model.direction == 0:
            x_axes = [scened_x + axis for axis in self.model.additive_axes]
            y_axes = [scened_y + axis for axis in self.model.solvent_axes]
        else:
            x_axes = [scened_x + axis for axis in self.model.solvent_axes]
            y_axes = [scened_y + axis for axis in self.model.additive_axes]
        self.border.set_circles_center(x_axes, y_axes)

    def set_circle_radius(self, radius):
        self.border.set_circle_radius(radius)

    def get_district(self):
        x, y = self.model.area_x, self.model.area_y
        width, height = self.model.area_width, self.model.area_height
        direction, rotation = self.model.direction, self.model.rotation
        additive_axes, solvent_axes = self.model.additive_axes, self.model.solvent_axes

        return x, y, width, height, direction, rotation, additive_axes, solvent_axes

    def set_masking_view(self, masking_view):
        self.view.scene.masking_view.setPixmap(masking_view)


def main():
    app = QApplication([])
    widget = QWidget()
    image = QImage("../../../plate_image.jpg")
    district = MaskGraphicsWidget(image)
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
