import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget

from ui.common import BaseWidgetView, BaseController, ColoredButton, ImageButton
from util.camera_manager import CameraManager

from util import local_storage_manager as lsm


class ImageViewerModel:
    def __init__(self):
        pass


class ImageViewerView(BaseWidgetView):
    camera_manager = CameraManager()

    def __init__(self, parent=None):
        super().__init__(parent)

        style = "border: 1px solid black; font-size:18px; font-weight: bold;"
        self.lb = QLabel("NO CAMERA")
        self.lb.setStyleSheet(style)
        self.lb.setAlignment(Qt.Alignment.AlignCenter)
        self.lb.setFixedSize(360, 540)

        img_rotate = lsm.get_static_image_path("rotate-right-90.png")
        self.btn_refresh = ColoredButton("카메라 재연결", background_color="gray", padding="10px")
        self.btn_rotate = ImageButton(image=img_rotate, size=(35, 35))
        self.btn_capture = ColoredButton("캡처", padding="10px")
        self.btn_refresh.clicked.connect(self.on_refresh_clicked)
        self.btn_rotate.clicked.connect(self.camera_manager.set_direction)

        wig_btn = QWidget()
        lyt_btn = QHBoxLayout(wig_btn)
        lyt_btn.addWidget(self.btn_refresh)
        # lyt_btn.addWidget(self.btn_capture)
        lyt_btn.addWidget(self.btn_rotate)
        lyt_btn.setAlignment(Qt.AlignCenter)
        lyt_btn.setContentsMargins(0, 0, 0, 0)

        lyt = QVBoxLayout(self)
        lyt.addStretch()
        lyt.addWidget(wig_btn)
        lyt.addWidget(self.lb)
        lyt.addWidget(self.btn_capture)
        lyt.addStretch()

        self.setMinimumHeight(700)

        self.camera_manager.signal_image.connect(self.update_image)

    def init_view(self):
        super().init_view()

    def update_image(self, image: np.ndarray):
        if image is not None:
            qimage = QImage(image.data, image.shape[1], image.shape[0], (image.shape[1] * 24 + 31) // 32 * 4,
                            QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            self.lb.setPixmap(pixmap.scaled(self.lb.size(), Qt.KeepAspectRatio))

    def on_refresh_clicked(self):
        self.lb.setText("NO CAMERA")
        self.camera_manager.connect_to_camera()


class ImageViewerController(BaseController):
    capture_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(ImageViewerModel, ImageViewerView, parent)

    def init_controller(self):
        super().init_controller()

        view: ImageViewerView = self.view
        view.btn_capture.clicked.connect(self.capture_clicked.emit)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ImageViewerController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
