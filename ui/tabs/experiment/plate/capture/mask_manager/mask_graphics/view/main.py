from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsSceneMouseEvent, QGraphicsPixmapItem

from ui.tabs.experiment.plate.capture.mask_manager.mask_graphics.view.mask_district_border import MaskDistrictBorder


class MaskGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing, True)
        self.scene = None

    def set_scene(self, origin_image):
        self.scene = MaskGraphicsScene(origin_image)
        self.setScene(self.scene)

    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)


class MaskGraphicsScene(QGraphicsScene):
    mouse_moved_signal = Signal(QGraphicsSceneMouseEvent)
    mouse_pressed_signal = Signal(QGraphicsSceneMouseEvent)
    mouse_released_signal = Signal(QGraphicsSceneMouseEvent)

    def __init__(self, origin_image, parent=None):
        super().__init__(parent)

        self.origin_view = QGraphicsPixmapItem(QPixmap.fromImage(origin_image))
        self.masking_view = QGraphicsPixmapItem(QPixmap.fromImage(origin_image))
        self.addItem(self.origin_view)
        self.addItem(self.masking_view)

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
