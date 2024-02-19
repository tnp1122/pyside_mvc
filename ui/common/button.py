import os

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QPixmap, QIcon, QTransform
from PySide6.QtWidgets import QPushButton, QApplication, QWidget, QVBoxLayout, QLabel


class ImageButton(QPushButton):
    def __init__(self, text=None, image=None, size=None, degree=0, parent=None):
        super().__init__(text, parent)

        if image:
            if isinstance(image, QPixmap):
                self.pixmap = image
            else:
                self.pixmap = QPixmap(image)

            self.set_transformed_icon(degree)
            if size:
                icon_size = QSize(*size)
            else:
                icon_size = self.pixmap.rect().size()
            self.setIconSize(icon_size)
            self.setFixedSize(icon_size)
        self.setStyleSheet("""
            QPushButton {
                border: 0px;
            }
        """)

    def set_transformed_icon(self, degree):
        rotated_pixmap = self.pixmap.transformed(QTransform().rotate(degree))
        self.setIcon(QIcon(rotated_pixmap))


class ColoredButton(QPushButton):
    def __init__(self, text, color=None, background_color=None, padding=None, parent=None):
        super().__init__(text, parent)
        style = f"""
            color: {color or "white"};
            background-color: {background_color or "#5E6C80"};
            border: 0px;
            padding: {padding or "5px"};
        """
        self.setStyleSheet(style)


class CurvedCornerButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setStyleSheet("""
            border: 1px solid;
            border-radius: 5px;
            padding: 3px;
        """)


class RefreshButton(ImageButton):
    def __init__(self):
        img = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           "../../static/image/refresh.png")
        super().__init__(image=img)


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, event):
        self.clicked.emit()
        super().mouseDoubleClickEvent(event)


def main():
    app = QApplication([])
    image = "../../static/image/cogwheel.png"
    widget = QWidget()
    lyt = QVBoxLayout(widget)

    image_btn = ImageButton(image=image)
    curved_btn = CurvedCornerButton("곡선 버튼")
    colored_btn = ColoredButton("색 버튼")

    lyt.addWidget(image_btn)
    lyt.addWidget(curved_btn)
    lyt.addWidget(colored_btn)

    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
