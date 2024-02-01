from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QPushButton, QApplication, QWidget, QVBoxLayout


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


class ColoredButton(QPushButton):
    def __init__(self, text, color=None, background_color=None, parent=None):
        super().__init__(text, parent)
        style = f"""
            color: {color or "white"};
            background-color: {background_color or "#5E6C80"};
            border: 0px;
            padding: 5px;
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
