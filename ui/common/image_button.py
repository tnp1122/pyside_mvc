from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QPushButton, QApplication


class ImageButton(QPushButton):
    def __init__(self, text=None, image=None, size=None, parent=None):
        super().__init__(text, parent)

        if image:
            if isinstance(image, QPixmap):
                pixmap = image
            else:
                pixmap = QPixmap(image)
            self.setIcon(QIcon(pixmap))
            if size:
                icon_size = QSize(*size)
            else:
                icon_size = pixmap.rect().size()
            self.setIconSize(icon_size)
            self.setFixedSize(icon_size)
        self.setStyleSheet("""
            QPushButton {
                border: 0px;
            }
        """)


def main():
    app = QApplication([])
    image = "../../static/image/cogwheel.png"
    widget = ImageButton(image=image)
    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
