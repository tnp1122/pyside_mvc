from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem

from models.snapshot import PlatePosition, Snapshot, Mask


class MaskArea(QGraphicsRectItem):
    def __init__(self, snapshot: Snapshot, parent=None):
        self.snapshot = snapshot

        plate: PlatePosition = self.snapshot.plate_position
        self.direction = plate.direction
        x, y, width, height = plate.get_crop_area()

        super().__init__(x, y, width, height, parent)

        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.border = Border(x, y, width, height, self)

        pen = QPen(Qt.NoPen)
        self.setPen(pen)

        self.additive_axis_graphics = []  # 가로 플레이트에서 로우, 세로 플레이트에서 컬럼
        self.solvent_axis_graphics = []  # 가로 플레이트에서 컬럼, 세로 플레이트에서 로우
        self.circles = []

        plate.position_changed.connect(self.on_position_changed)
        plate.direction_changed.connect(self.update_direction)

        mask: Mask = self.snapshot.mask
        mask.radius_changed.connect(lambda: self.update_circle_radius(mask))

        self.init_graphics()

    def init_graphics(self):
        plate: PlatePosition = self.snapshot.plate_position
        mask: Mask = self.snapshot.mask

        additive_axes, solvent_axes = plate.additive_axes, plate.solvent_axes
        vertical_add = self.direction != 0
        vertical_sol = self.direction == 0
        self.additive_axis_graphics = [Axis(is_vertical=vertical_add, is_additive=True, parent=self) for _ in
                                       additive_axes]
        self.solvent_axis_graphics = [Axis(is_vertical=vertical_sol, parent=self) for _ in solvent_axes]
        self.circles = [Circle(parent=self) for _ in range(len(solvent_axes) * len(additive_axes))]

        self.set_circle_visible(False)
        self.update_circle_radius(mask)
        self.on_position_changed(True)

        self.set_movable(False)

    def set_circle_visible(self, is_visible):
        for circle in self.circles:
            circle.setVisible(is_visible)

    def set_movable(self, movable):
        self.setFlag(QGraphicsRectItem.ItemIsMovable, movable)

    def toggle_direction(self):
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        self.setRect(y, x, h, w)

    def update_direction(self, direction):
        if self.direction == direction:
            return
        self.direction = direction
        self.toggle_direction()
        self.border.toggle_direction()
        for solvent in self.solvent_axis_graphics:
            solvent.toggle_direction()
        for additive in self.additive_axis_graphics:
            additive.toggle_direction()
        for circle in self.circles:
            circle.toggle_direction()

        self.snapshot.plate_position.set_position_with_qrect(self.rect(), update_graphics=False)

    def on_position_changed(self, update_graphics: bool):
        if not update_graphics:
            return

        plate: PlatePosition = self.snapshot.plate_position

        x, y, width, height = plate.get_crop_area()
        self.setRect(x, y, width, height)
        self.border.setRect(x, y, width, height)

        x, y, width, height = plate.get_axis_position()
        solvent_axes = plate.solvent_axes
        additive_axes = plate.additive_axes
        for index, axis in enumerate(self.solvent_axis_graphics):
            value = x + solvent_axes[index]
            axis: Axis
            axis.set_value(value, False)
            axis.set_start(y, False)
            axis.set_height(height)

        for index, axis in enumerate(self.additive_axis_graphics):
            value = y + additive_axes[index]
            axis: Axis
            axis.set_value(value, False)
            axis.set_start(x, False)
            axis.set_height(width)

        len_additive = len(additive_axes)
        for i, solvent_axis in enumerate(solvent_axes):
            for j, additive_axis in enumerate(additive_axes):
                index = i * len_additive + j
                solvent = x + solvent_axis
                additive = y + additive_axis

                if self.direction == 0:
                    self.circles[index].set_center(solvent, additive)
                else:
                    self.circles[index].set_center(additive, solvent)

    def update_circles_center(self, plate: PlatePosition):
        x_len = len(plate.columns)
        for y_idx, y in enumerate(plate.rows):
            for x_idx, x in enumerate(plate.columns):
                idx = x_idx + y_idx * x_len
                self.circles[idx].set_center(plate.x + x, plate.y + y)

    def update_circle_radius(self, arg: Union[int, Mask]):
        if isinstance(arg, int):
            radius = arg
        else:
            radius = arg.radius
        for circle in self.circles:
            circle.set_radius(radius)


class Border(QGraphicsRectItem):
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(x, y, width, height, parent)

        self.border_width = 10
        pen = QPen(Qt.red)
        pen.setWidth(self.border_width)
        self.setPen(pen)
        self.setBrush(QBrush(Qt.NoBrush))
        self.setAcceptHoverEvents(True)

    def toggle_direction(self):
        rect = self.rect()
        x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
        self.setRect(y, x, height, width)


class Axis(QGraphicsRectItem):
    def __init__(
            self,
            value=0,
            bar_start=0,
            head_width=20,
            head_height=50,
            bar_width=10,
            bar_height=10,
            is_vertical=False,
            is_additive=False,
            parent=None
    ):
        super().__init__(parent)
        self.value = value
        self.bar_start = bar_start
        self.head_width = head_width
        self.head_height = head_height
        self.bar_width = bar_width
        self.bar_height = bar_height
        self.is_vertical = is_vertical
        self.is_additive = is_additive
        if is_additive:
            self.brush = QBrush(QColor(255, 255, 0))
            self.setZValue(0)
        else:
            self.brush = QBrush(QColor(0, 255, 0))
            self.setZValue(1)
        self.head = QGraphicsRectItem(self)
        self.bar = QGraphicsRectItem(self)

        self.head.setPen(Qt.NoPen)
        self.head.setBrush(self.brush)
        self.bar.setPen(Qt.NoPen)
        self.bar.setBrush(self.brush)
        self.update_pos()

    def update_pos(self):
        if self.is_vertical:
            head_x = self.value - self.head_width / 2
            head_y = self.bar_start - self.head_height
            head_width = self.head_width
            head_height = self.head_height
            bar_x = self.value - self.bar_width / 2
            bar_y = self.bar_start
            bar_width = self.bar_width
            bar_height = self.bar_height
        else:
            if self.is_additive:
                head_x = self.bar_start + self.bar_height
            else:
                head_x = self.bar_start - self.head_height
            head_y = self.value - self.head_width / 2
            head_width = self.head_height
            head_height = self.head_width
            bar_x = self.bar_start
            bar_y = self.value - self.bar_width / 2
            bar_width = self.bar_height
            bar_height = self.bar_width

        self.head.setRect(head_x, head_y, head_width, head_height)
        self.bar.setRect(bar_x, bar_y, bar_width, bar_height)

    def toggle_direction(self):
        self.is_vertical = not self.is_vertical
        self.update_pos()

    def set_value(self, value, update=True):
        self.value = value
        if update:
            self.update_pos()

    def set_start(self, start, update=True):
        self.bar_start = start
        if update:
            self.update_pos()

    def set_height(self, height, update=True):
        self.bar_height = height
        if update:
            self.update_pos()


class Circle(QGraphicsEllipseItem):
    def __init__(self, cx=0, cy=0, radius=10, parent=None):
        super().__init__(cx - radius, cy - radius, 2 * radius, 2 * radius, parent)
        self.setPen(Qt.NoPen)
        self.setBrush(Qt.white)
        self.setZValue(2)

    def center(self):
        rect = self.rect()
        cx = rect.x() + rect.width() / 2
        cy = rect.y() + rect.height() / 2
        return cx, cy

    def radius(self):
        return self.rect().width() / 2

    def toggle_direction(self):
        x, y = self.center()
        self.set_center(y, x)

    def set_center(self, x, y):
        rect = self.rect()
        cx = x - self.radius()
        cy = y - self.radius()
        self.setRect(cx, cy, rect.width(), rect.height())

    def set_radius(self, radius):
        center = self.center()
        cx = center[0] - radius
        cy = center[1] - radius
        self.setRect(cx, cy, radius * 2, radius * 2)
