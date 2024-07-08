import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout

from util import local_storage_manager as lsm


class LoadingSpinner(QWidget):
    _instance = None
    angle = 360
    rotate_velocity = 60

    def __new__(cls, parent=None):
        if not cls._instance:
            cls._instance = super(LoadingSpinner, cls).__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if hasattr(self, "initialized") or parent is None:
            return
        super().__init__(parent)

        self.label = QLabel("dd")
        self.label.setAlignment(Qt.AlignCenter)
        image_path = lsm.get_static_image_path("loading_spinner.png")

        self.pixmap = QPixmap(image_path).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)

        lyt = QVBoxLayout(self)
        lyt.setAlignment(Qt.AlignCenter)
        lyt.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_image)

        self.initialized = True
        self.setVisible(False)

    def start_loading(self):
        self.setVisible(True)
        self.timer.start(100)

    def end_loading(self):
        self.timer.stop()
        self.setVisible(False)
        self.angle = 0

    def rotate_image(self):
        self.angle += self.rotate_velocity
        if self.angle >= 360:
            self.angle -= 360

        transform = QTransform().rotate(self.angle)
        rotated_pixmap = self.pixmap.transformed(transform, Qt.SmoothTransformation)
        self.label.setPixmap(rotated_pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = LoadingSpinner()
    widget.show()

    sys.exit(app.exec())
