import PySide6
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QPen, QBrush, QColor, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsView


class MaskDistrictView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.scene = None

    def set_scene(self, origin_image):
        self.scene = MaskDistrictScene(origin_image)
        self.setScene(self.scene)

    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)


class MaskDistrictScene(QGraphicsScene):
    mouse_moved_signal = Signal(PySide6.QtWidgets.QGraphicsSceneMouseEvent)
    mouse_pressed_signal = Signal(PySide6.QtWidgets.QGraphicsSceneMouseEvent)
    mouse_released_signal = Signal(PySide6.QtWidgets.QGraphicsSceneMouseEvent)

    def __init__(self, origin_image, parent=None):
        super().__init__(parent)

        pixmap = QPixmap.fromImage(origin_image)
        self.addPixmap(pixmap)

        self.border = None

    def add_border(self, x, y, width, height, border_width):
        self.border = MaskDistrictBorder(x, y, width, height, border_width)
        self.addItem(self.border)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.mouse_moved_signal.emit(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.mouse_pressed_signal.emit(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.mouse_released_signal.emit(event)


class MaskDistrictBorder(QGraphicsRectItem):
    def __init__(self, x, y, width, height, border_width, parent=None):
        super().__init__(x, y, width, height, parent)

        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setTransformOriginPoint(self.rect().center())

        pen = QPen(Qt.NoPen)
        self.setPen(pen)

        self.mask_area = MaskDistrictArea(x, y, width, height, border_width, self)
        self.vertical_axes = [Axis(0, y, head_height=50, bar_height=height, is_vertical=True, parent=self) for _ in
                              range(12)]
        self.horizontal_axes = [Axis(0, x, head_height=50, bar_height=width, parent=self) for _ in range(12)]
        self.circles = [Circle(x, y, 10, self) for y in range(8) for x in range(12)]

    def set_circle_visible(self, is_visible):
        for circle in self.circles:
            circle.setVisible(is_visible)

    def set_movable(self, movable):
        self.setFlag(QGraphicsRectItem.ItemIsMovable, movable)

    def set_direction(self, direction):
        if direction == 0:
            for axis in self.vertical_axes[-4:]:
                axis.setVisible(True)
            for axis in self.horizontal_axes[-4:]:
                axis.setVisible(False)

        else:
            for axis in self.vertical_axes[-4:]:
                axis.setVisible(False)
            for axis in self.horizontal_axes[-4:]:
                axis.setVisible(True)

    def set_bar_height(self, value, diff, is_vertical=True):
        if is_vertical:
            axes = self.vertical_axes
        else:
            axes = self.horizontal_axes
        for axis in axes:
            head = axis.head.rect()
            bar = axis.bar.rect()

            if is_vertical:
                head_x = head.x()
                head_y = head.y() - diff
                bar_x = bar.x()
                bar_y = bar.y() - diff
                width = bar.width()
                height = value
            else:
                head_x = head.x() - diff
                head_y = head.y()
                bar_x = bar.x() - diff
                bar_y = bar.y()
                width = value
                height = bar.height()

            axis.head.setRect(head_x, head_y, head.width(), head.height())
            axis.bar.setRect(bar_x, bar_y, width, height)

    def set_intervals(self, axes, is_up_down_interval=True):
        if is_up_down_interval:
            axis_bars = self.horizontal_axes
        else:
            axis_bars = self.vertical_axes

        for idx, value in enumerate(axes):
            axis_bars[idx].set_pos(value)

    def set_circles_center(self, x_axes, y_axes):
        x_len = len(x_axes)
        for y_idx, y in enumerate(y_axes):
            for x_idx, x in enumerate(x_axes):
                idx = x_idx + y_idx * x_len
                self.circles[idx].set_center(x, y)

    def set_circle_radius(self, radius):
        for circle in self.circles:
            circle.set_radius(radius)


class MaskDistrictArea(QGraphicsRectItem):
    def __init__(self, x, y, width, height, border_width, parent=None):
        super().__init__(x, y, width, height, parent)

        pen = QPen(Qt.red)
        pen.setWidth(border_width)
        self.setPen(pen)
        self.setBrush(QBrush(Qt.NoBrush))
        self.setAcceptHoverEvents(True)
        self.resize_origin = None
        self.rotate_origin = None


class Axis(QGraphicsRectItem):
    def __init__(self, value, bar_start, head_width=20, head_height=10, bar_width=10, bar_height=10, is_vertical=False,
                 parent=None):
        super().__init__(parent)
        self.value = value
        self.is_vertical = is_vertical
        if is_vertical:
            head_x = value - head_width / 2
            head_y = bar_start - head_height
            bar_x = value - bar_width / 2
            bar_y = bar_start

            self.head = QGraphicsRectItem(head_x, head_y, head_width, head_height, self)
            self.bar = QGraphicsRectItem(bar_x, bar_y, bar_width, bar_height, self)
            self.brush = QBrush(QColor(255, 255, 0))
        else:
            head_x = bar_start - head_height
            head_y = value - head_width / 2
            bar_x = bar_start
            bar_y = value - bar_width / 2

            self.head = QGraphicsRectItem(head_x, head_y, head_height, head_width, self)
            self.bar = QGraphicsRectItem(bar_x, bar_y, bar_height, bar_width, self)
            self.brush = QBrush(QColor(0, 255, 0))

        self.head.setPen(Qt.NoPen)
        self.head.setBrush(self.brush)
        self.bar.setPen(Qt.NoPen)
        self.bar.setBrush(self.brush)

    def set_pos(self, value):
        self.value = value
        head = self.head.rect()
        bar = self.bar.rect()

        if self.is_vertical:
            head_x = value - head.width() / 2
            head_y = head.y()
            bar_x = value - bar.width() / 2
            bar_y = bar.y()

        else:
            head_x = head.x()
            head_y = value - head.height() / 2
            bar_x = bar.x()
            bar_y = value - bar.height() / 2

        self.head.setRect(head_x, head_y, head.width(), head.height())
        self.bar.setRect(bar_x, bar_y, bar.width(), bar.height())


class Circle(QGraphicsEllipseItem):
    def __init__(self, cx, cy, radius, parent=None):
        super().__init__(cx - radius, cy - radius, 2 * radius, 2 * radius, parent)
        self.setPen(Qt.NoPen)
        self.setBrush(Qt.white)

    def center(self):
        rect = self.rect()
        cx = rect.x() + rect.width() / 2
        cy = rect.y() + rect.height() / 2
        return cx, cy

    def radius(self):
        return self.rect().width() / 2

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
