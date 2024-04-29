from typing import Union

from PySide6.QtCore import QSize, Qt, Signal, QEvent, QPropertyAnimation, QPoint
from PySide6.QtGui import QPixmap, QIcon, QMouseEvent
from PySide6.QtWidgets import QPushButton, QApplication, QWidget, QVBoxLayout, QLabel

from util import local_storage_manager as lsm


class ImageButton(QPushButton):
    def __init__(self, image: Union[str, QPixmap, QIcon], size=None, padding=(0, 0, 0, 0), parent=None):
        super().__init__(parent=parent)

        self.set_icon(image, size, padding)

    def set_icon(self, image: Union[str, QPixmap, QIcon], size=None, padding=(0, 0, 0, 0)):
        if isinstance(image, QIcon):
            self.setIcon(image)
        else:
            if isinstance(image, QPixmap):
                pixmap = image
            else:
                pixmap = QPixmap(image)
            self.setIcon(pixmap)

        if size:
            icon_size = QSize(*size)
        else:
            icon_size = self.iconSize()

        widget_size = (icon_size.width() + padding[1] + padding[3], icon_size.height() + padding[0] + padding[2])
        self.setIconSize(icon_size)
        self.setFixedSize(*widget_size)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; 
                border: none;
                padding-top: {padding[0]};
                padding-right: {padding[1]};
                padding-bottom: {padding[2]};
                padding-left: {padding[3]};
            }}
        """)


class ColoredButton(QPushButton):
    def __init__(
            self,
            text,
            size=None,
            color=None,
            background_color=None,
            padding=None,
            border_thickness=None,
            border_color=None,
            parent=None
    ):
        super().__init__(text, parent)
        if size:
            self.setFixedSize(*size)
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
    label_clicked = Signal(QMouseEvent)

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.rect().contains(event.position().toPoint(), True):
            if event.button() == Qt.LeftButton:
                if event.modifiers() == Qt.NoModifier:
                    if event.type() == QEvent.MouseButtonRelease:
                        self.label_clicked.emit(event)

        super().mouseReleaseEvent(event)


class Toggle(QWidget):
    widget_clicked = Signal(QMouseEvent)

    def __init__(self, text_left="", text_right="", size: tuple = None, parent=None):
        super().__init__(parent)

        size = size if size else (100, 30)

        self.radius = int(size[1] / 2)
        self.switch_padding = 3
        self.switch_radius = self.radius - self.switch_padding
        self.label_size = (size[0] - self.radius * 2 - self.switch_padding, size[1] - self.switch_padding * 2)

        self.toggle_left = True
        self.text_left = text_left
        self.text_right = text_right
        self.color_left = "#2962A5"
        self.color_right = "#00A368"

        self.setFixedSize(*size)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("toggle")
        self.setStyleSheet(
            f"""
            #toggle {{
                background-color: {self.color_left};
                border-radius: {self.radius}px;
            }}
            """
        )

        self.lb = QLabel(text_left, self)
        self.lb.setFixedSize(*self.label_size)
        self.lb.setAlignment(Qt.AlignCenter)
        self.lb.setStyleSheet("color: white;")

        self.switch = QWidget(self)
        self.switch.setFixedSize(self.switch_radius * 2, self.switch_radius * 2)
        self.switch.setStyleSheet(f"border-radius: {self.switch_radius}px; background-color: white;")

        pos_lb = (self.switch_padding, self.switch_padding)
        pos_switch = self.size().width() - self.switch_padding - self.switch_radius * 2, self.switch_padding
        self.lb.move(*pos_lb)
        self.switch.move(*pos_switch)
        # self.toggle()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.rect().contains(event.position().toPoint(), True):
            if event.button() == Qt.LeftButton:
                if event.modifiers() == Qt.NoModifier:
                    if event.type() == QEvent.MouseButtonRelease:
                        self.widget_clicked.emit(event)
                        self.toggle()

        super().mouseReleaseEvent(event)

    def toggle(self):
        self.toggle_left = not self.toggle_left
        if self.toggle_left:
            self.setStyleSheet(
                f"""
                #toggle {{
                    background-color: {self.color_left};
                    border-radius: {self.radius}px;
                }}
                """
            )
            self.lb.setText(self.text_left)
            pos_lb = (self.switch_padding, self.switch_padding)
            self.lb.move(*pos_lb)
            self.animation = QPropertyAnimation(self.switch, b"pos")
            pos_switch = QPoint(self.size().width() - self.switch_padding - self.switch_radius * 2, self.switch_padding)
            self.animation.setEndValue(pos_switch)
            self.animation.setDuration(200)
            self.animation.start()
        else:
            self.setStyleSheet(
                f"""
                #toggle {{
                    background-color: {self.color_right};
                    border-radius: {self.radius}px;
                }}
                """
            )
            self.lb.setText(self.text_right)
            pos_lb = ((self.switch_radius + self.switch_padding) * 2, self.switch_padding)
            self.lb.move(*pos_lb)
            self.animation = QPropertyAnimation(self.switch, b"pos")
            pos_switch = QPoint(self.switch_padding, self.switch_padding)
            self.animation.setEndValue(pos_switch)
            self.animation.setDuration(200)
            self.animation.start()


def main():
    app = QApplication([])
    app.setStyleSheet("")
    image = "../../static/image/cogwheel.png"
    widget = QWidget()
    lyt = QVBoxLayout(widget)
    lyt.setContentsMargins(10, 10, 10, 10)
    lyt.setSpacing(10)

    image_btn = ImageButton(image=image, padding=(30, 150, 50, 10))
    curved_btn = CurvedCornerButton("곡선 버튼")
    colored_btn = ColoredButton("색 버튼")
    border_btn = ColoredButton("테두리", border_thickness="1px")

    toggle = Toggle("스", "타임라인")
    # toggle2 = Toggle2("비교 촬영", "타임라인")

    lyt.addWidget(image_btn)
    lyt.addWidget(curved_btn)
    lyt.addWidget(colored_btn)
    lyt.addWidget(border_btn)
    lyt.addWidget(toggle)
    # lyt.addWidget(toggle2)

    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
