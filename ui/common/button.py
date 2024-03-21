from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QPixmap, QIcon, QTransform
from PySide6.QtWidgets import QPushButton, QApplication, QWidget, QVBoxLayout, QLabel

from util import local_storage_manager as lsm


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
    def __init__(self, text, color=None, background_color=None, padding=None, border_thickness=None, border_color=None, parent=None):
        super().__init__(text, parent)
        self.color = color or "white"
        self.background_color = background_color or "#5E6C80"
        self.padding = padding or "5px"
        self.border_thickness = border_thickness or "0px"
        self.border_color = border_color or "black"

        self.set_style()

    def set_style(self):
        style = f"""
            color: {self.color};
            background-color: {self.background_color};
            border: 0px;
            padding: {self.padding};
            border: {self.border_thickness} solid {self.border_color};
        """
        self.setStyleSheet(style)

    def set_color(self, color=None):
        self.color = color or "white"
        self.set_style()

    def set_background_color(self, background_color=None):
        self.background_color = background_color or "#5E6C80"
        self.set_style()

    def set_padding(self, padding=None):
        self.padding = padding or "5px"
        self.set_style()

    def set_border(self, border_thickness, border_color):
        self.border_thickness = border_thickness
        self.border_color = border_color
        self.set_style()


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
        img = lsm.get_static_image_path("refresh.png")
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
    border_btn = ColoredButton("테두리", border_thickness="1px")

    lyt.addWidget(image_btn)
    lyt.addWidget(curved_btn)
    lyt.addWidget(colored_btn)
    lyt.addWidget(border_btn)

    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
