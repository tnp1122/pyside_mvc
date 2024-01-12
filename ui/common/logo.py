import os.path

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap


class Logo(QLabel):
    def __init__(self, with_title=False, parent=None):
        super().__init__(parent)
        if with_title:
            image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                      "../../static/image/logo_with_title.png")
        else:
            image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../static/image/logo.png")

        logo = QPixmap(image_path)
        self.setPixmap(logo)
