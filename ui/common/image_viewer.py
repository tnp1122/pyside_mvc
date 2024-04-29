import numpy as np
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget

from model import Image
from ui.common import BaseWidgetView, BaseController, ColoredButton, ImageButton
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import MaskManagerController
from util.camera_manager import CameraManager

from util import local_storage_manager as lsm
from util import image_converter as ic
from util.setting_manager import SettingManager


class ImageViewerModel:
    def __init__(self):
        pass


class ImageViewerView(BaseWidgetView):
    camera_manager = CameraManager()

    # mode 0: 스냅샷 촬영, mode 1: 타임라인 촬영
    def __init__(self, parent=None, mode=0):
        super().__init__(parent)

        self.view_mask = False
        self.mask_area = None

        self.image: np.ndarray = None
        img_setting = lsm.get_static_image_path("filter.png")
        self.img_view = lsm.get_static_image_path("view.png")
        self.img_view_hide = lsm.get_static_image_path("view_hide.png")
        img_rotate = lsm.get_static_image_path("rotate-right-90.png")
        self.btn_refresh = ColoredButton("카메라 재연결", background_color="gray", padding="10px")
        self.btn_setting = ImageButton(img_setting, size=(35, 35))
        self.btn_setting.setToolTip("마스크 설정")
        self.btn_view_mask = ImageButton(self.img_view_hide, size=(30, 30))
        self.btn_view_mask.setToolTip("마스킹 영역 보이기")
        self.btn_rotate = ImageButton(img_rotate, size=(30, 30))
        self.btn_rotate.setToolTip("시계 방향으로 90도 회전")
        self.btn_refresh.clicked.connect(self.on_refresh_clicked)
        self.btn_setting.clicked.connect(self.open_mask_manager)
        self.btn_view_mask.clicked.connect(self.on_view_mask_clicked)
        self.btn_rotate.clicked.connect(self.camera_manager.set_direction)

        wig_btn = QWidget()
        lyt_btn = QHBoxLayout(wig_btn)
        lyt_btn.addWidget(self.btn_refresh)
        lyt_btn.addWidget(self.btn_setting)
        lyt_btn.addWidget(self.btn_view_mask)
        lyt_btn.addWidget(self.btn_rotate)
        lyt_btn.setAlignment(Qt.AlignCenter)
        lyt_btn.setContentsMargins(0, 0, 0, 0)

        style = "border: 1px solid black; font-size:18px; font-weight: bold;"
        self.lb = QLabel("NO CAMERA")
        self.lb.setStyleSheet(style)
        self.lb.setAlignment(Qt.Alignment.AlignCenter)
        self.lb.setFixedSize(360, 540)

        self.btn_capture = ColoredButton("캡처", padding="10px")
        self.btn_run_timeline = ColoredButton("타임라인 촬영 시작", padding="10px")

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addStretch()
        lyt.addWidget(wig_btn)
        lyt.addWidget(self.lb)
        lyt.addWidget(self.btn_capture)
        lyt.addWidget(self.btn_run_timeline)
        lyt.addStretch()

        if mode == 0:
            self.btn_setting.setVisible(False)
            self.btn_view_mask.setVisible(False)
            self.btn_run_timeline.setVisible(False)
        else:
            self.btn_capture.setVisible(False)

        self.camera_manager.signal_image.connect(self.update_image)

    def init_view(self):
        super().init_view()

    def update_image(self, image: np.ndarray):
        if image is not None:
            self.image = image
            pixmap = ic.array_to_q_pixmap(image, True)

            if self.view_mask:
                painter = QPainter(pixmap)
                painter.setPen(QPen(Qt.red, 5))
                painter.drawRect(self.mask_area)
                painter.end()

            self.lb.setPixmap(pixmap.scaled(self.lb.size(), Qt.KeepAspectRatio))

    def on_refresh_clicked(self):
        self.lb.setText("NO CAMERA")
        self.camera_manager.connect_to_camera()

    def open_mask_manager(self):
        if self.image is not None:
            self.mask_manager = MaskManagerController(origin_image=Image(self.image))
            self.mask_manager.view.btn_apply.clicked.connect(self.on_mask_apply_clicked)
            self.mask_manager.view.exec()

    def get_mask_area_info(self):
        self.mask_area_info = SettingManager().get_mask_area_info()
        x, y = self.mask_area_info["x"], self.mask_area_info["y"]
        if self.mask_area_info["direction"] == 0:
            width, height = self.mask_area_info["width"], self.mask_area_info["height"]
        else:
            width, height = self.mask_area_info["height"], self.mask_area_info["width"]

        self.mask_area = QRect(x, y, width, height)
        # return self.mask_area

    def on_mask_apply_clicked(self):
        self.get_mask_area_info()
        self.mask_manager.close()

    def on_view_mask_clicked(self):
        self.view_mask = not self.view_mask

        if self.view_mask:
            self.btn_view_mask.set_icon(self.img_view)
            self.btn_view_mask.setToolTip("마스킹 영역 숨기기")
            self.get_mask_area_info()
        else:
            self.btn_view_mask.set_icon(self.img_view_hide)
            self.btn_view_mask.setToolTip("마스킹 영역 보이기")


class ImageViewerController(BaseController):
    capture_clicked = Signal()
    run_timeline_clicked = Signal(bool)

    def __init__(self, parent=None, mode=0):
        super().__init__(ImageViewerModel, ImageViewerView, parent, mode)

    def init_controller(self):
        super().init_controller()

        self.is_running_timeline = False

        view: ImageViewerView = self.view
        view.btn_capture.clicked.connect(self.capture_clicked.emit)
        view.btn_run_timeline.clicked.connect(self.switch_run_timeline)

    def switch_run_timeline(self):
        self.is_running_timeline = not self.is_running_timeline

        view: ImageViewerView = self.view
        if self.is_running_timeline:
            btn_text = "타임라인 촬영 시작"
        else:
            btn_text = "타임라인 촬영 중단"
        view.btn_run_timeline.setText(btn_text)

        self.run_timeline_clicked.emit(self.is_running_timeline)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ImageViewerController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
