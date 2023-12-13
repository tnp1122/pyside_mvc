import PySide6
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QPixmap, QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem


class MaskDistrictView(QGraphicsView):
    ui_initialized_signal = Signal()

    def __init__(self, origin_image, parent=None):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.scene = MaskDistrictScene(origin_image)

        self.setScene(self.scene)
        self.ui_initialized_signal.emit()

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

    def add_border(self, x, y, width, height, border_width, margin):
        self.border = MaskDistrictBorder(x, y, width, height, border_width, margin)
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
    def __init__(self, x, y, width, height, border_width, margin, parent=None):
        super().__init__(x, y, width, height, parent)
        self.margin = margin

        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setTransformOriginPoint(self.rect().center())

        pen = QPen(Qt.NoPen)
        self.setPen(pen)

        self.mask_area = None
        self.additive_axes = []
        self.solvent_axes = []

    def set_movable(self, movable):
        self.setFlag(QGraphicsRectItem.ItemIsMovable, movable)

    def add_mask_area(self, x, y, width, height, border_width):
        self.mask_area = MaskDistrictArea(x, y, width, height, border_width, self)

    def add_axes(self, value, bar_start, head_width, head_height, bar_width, bar_height, is_vertical=False):
        axis = Axis(value, bar_start, head_width, head_height, bar_width, bar_height, is_vertical, self)
        if is_vertical:
            self.additive_axes.append(axis)
        else:
            self.solvent_axes.append(axis)

    def set_interval(self, axes, is_vertical):
        if is_vertical:
            axes_bar = self.solvent_axes
        else:
            axes_bar = self.additive_axes

        for idx, axis in enumerate(axes_bar):
            axis.set_pos(axes[idx])


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
    def __init__(self, value, bar_start, head_width=10, head_height=10, bar_width=10, bar_height=10, is_vertical=False,
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

        self.head.setBrush(self.brush)
        self.bar.setBrush(self.brush)

    def set_height(self, value, diff):
        head = self.head.rect()
        bar = self.bar.rect()

        if self.is_vertical:
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

        self.head.setRect(head_x, head_y, head.width(), head.height())
        self.bar.setRect(bar_x, bar_y, width, height)
        return

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
