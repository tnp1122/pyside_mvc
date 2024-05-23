from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsPixmapItem

from models.snapshot import Snapshot
from ui.common import BaseGraphicsView
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics.view.mask_area import MaskArea


class MaskGraphicsView(BaseGraphicsView):
    def __init__(self, parent=None, snapshot: Snapshot = None):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing, True)

        self.scene = MaskGraphicsScene(snapshot)
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

    def __init__(self, snapshot: Snapshot, parent=None):
        super().__init__(parent)

        pixmap = snapshot.origin_image.q_pixmap
        self.snapshot = snapshot
        self.origin_view = QGraphicsPixmapItem(pixmap)
        self.masking_view = QGraphicsPixmapItem(pixmap)
        self.area = MaskArea(self.snapshot)

        self.addItem(self.origin_view)
        self.addItem(self.masking_view)
        self.addItem(self.area)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.mouse_moved_signal.emit(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.mouse_pressed_signal.emit(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.mouse_released_signal.emit(event)

    def update_masking_view(self):
        self.masking_view.setPixmap(self.snapshot.origin_sized_masked_pixmap)
