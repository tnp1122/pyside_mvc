from PySide6.QtCore import QTimer, Signal, QPropertyAnimation
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect


class Toast(QWidget):
    _instance = None
    toasted_signal = Signal()
    animation_duration = 300
    background_color = "#D9D9D9"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Toast, cls).__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if not hasattr(self, "initialized"):
            super().__init__(parent)
            self.setup_ui()

    def setup_ui(self):

        lyt = QVBoxLayout(self)
        self.lb = QLabel("")
        lyt.addWidget(self.lb)

        style = f"""
            background-color: {self.background_color};
            color: black;
            border: 1px solid {self.background_color};
            border-radius: 10px;
            padding: 10px;
        """
        self.setStyleSheet(style)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(self.animation_duration)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_toast)

        self.setVisible(False)

        self.initialized = True

    def toast(self, text="", duration=2500):
        self.lb.setText(text)
        self.resize(self.sizeHint())

        self.setVisible(True)
        self.fade_animation.setDirection(QPropertyAnimation.Forward)
        self.fade_animation.start()

        self.toasted_signal.emit()
        self.timer.start(duration)

    def hide_toast(self):
        self.timer.stop()

        self.fade_animation.setDirection(QPropertyAnimation.Backward)
        self.fade_animation.start()
        QTimer().singleShot(self.animation_duration, lambda: self.setVisible(False))


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = Toast()
    widget.toast("토스트", 1000)
    app.exec()


if __name__ == "__main__":
    main()
