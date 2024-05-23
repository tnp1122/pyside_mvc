from PySide6.QtGui import QImage
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from models.snapshot import Snapshot
from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics import MaskGraphicsModel, \
    MaskGraphicsView
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics.controller.mouse_handler import \
    MouseHandler
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics.controller.view_handler import \
    ViewHandler


class MaskGraphicsController(BaseController):
    def __init__(self, parent=None, snapshot: Snapshot = None):
        self.snapshot = snapshot

        super().__init__(MaskGraphicsModel, MaskGraphicsView, parent, snapshot)

        self.mouse_handler = MouseHandler(self)
        self.view_handler = ViewHandler(self.view)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = QWidget()
    image = QImage("../../../plate_image.jpg")
    district = MaskGraphicsController()
    district.set_scene(image)
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
