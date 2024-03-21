from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, Qt

from util import local_storage_manager as lsm


class Logo(QLabel):
    def __init__(self, with_title=False, parent=None, size=None):
        super().__init__(parent)
        if with_title:
            image_path = lsm.get_static_image_path("logo_with_title.png")
        else:
            image_path = lsm.get_static_image_path("logo.png")

        logo = QPixmap(image_path)

        if size:
            self.setPixmap(logo.scaled(*size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.setPixmap(logo)
