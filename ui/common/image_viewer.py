import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QPixmap
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget

from model import Image
from model.snapshot import Snapshot
from ui.common import BaseWidgetView, BaseController, ColoredButton, ImageButton
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import MaskManagerController, MaskManagerView
from util.camera_manager import CameraManager

from util import local_storage_manager as lsm
from util import image_converter as ic


class ImageViewerModel:
    def __init__(self):
        pass


class ImageViewerView(BaseWidgetView):
    camera_manager = CameraManager()
    instance_initialized = Signal()

    # mode 0: 스냅샷 촬영, mode 1: 타임라인 촬영
    def __init__(self, parent=None, args: dict = None):
        if args is not None:
            self.mode = args.get("mode")
            self.snapshot_instance: Snapshot = args.get("snapshot_instance")
            self.need_init = True
            self.sensor_indexes = []
            self.sensor_colors = []
        else:
            self.mode = 0
            self.snapshot_instance = None
            self.need_init = False

        super().__init__(parent)

        self.view_mask = True

        self.image: np.ndarray = None
        img_setting = lsm.get_static_image_path("filter.png")
        self.img_view = lsm.get_static_image_path("view.png")
        self.img_view_hide = lsm.get_static_image_path("view_hide.png")
        img_rotate = lsm.get_static_image_path("rotate-right-90.png")
        self.btn_refresh = ColoredButton("카메라 재연결", background_color="gray", padding="10px")
        self.btn_setting = ImageButton(img_setting, size=(35, 35))
        self.btn_setting.setToolTip("마스크 설정")
        self.btn_view_mask = ImageButton(self.img_view, size=(30, 30))
        self.btn_view_mask.setToolTip("마스킹 영역 숨기기")
        self.btn_rotate = ImageButton(img_rotate, size=(30, 30))
        self.btn_rotate.setToolTip("시계 방향으로 90도 회전")
        self.btn_refresh.clicked.connect(self.on_refresh_clicked)
        self.btn_setting.clicked.connect(self.open_mask_manager)
        self.btn_view_mask.clicked.connect(self.switch_view_mask)
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

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addStretch()
        lyt.addWidget(wig_btn)
        lyt.addWidget(self.lb)
        lyt.addWidget(self.btn_capture)
        lyt.addStretch()

        if self.mode == 0:
            self.btn_setting.setVisible(False)
            self.btn_view_mask.setVisible(False)
            self.btn_capture.setText("캡쳐")
        else:
            self.btn_capture.setText("타임라인 촬영 시작")

        self.camera_manager.signal_image.connect(self.update_image)

    def init_view(self):
        super().init_view()

    def update_image(self, image: np.ndarray):
        if image is not None:
            self.image = image
            pixmap = ic.array_to_q_pixmap(image, True)

            if self.need_init:
                snapshot: Snapshot = self.snapshot_instance
                snapshot.init_origin_image(Image(image))
                self.need_init = False
                self.instance_initialized.emit()

            if self.mode != 0 and self.view_mask:
                pixmap = self.paint_plate(pixmap)

            self.lb.setPixmap(pixmap.scaled(self.lb.size(), Qt.KeepAspectRatio))

    def paint_plate(self, pixmap: QPixmap) -> QPixmap:
        snapshot: Snapshot = self.snapshot_instance

        x, y, width, height = snapshot.plate_position.get_crop_area()
        r = snapshot.mask.radius
        row_axes = snapshot.plate_position.rows
        column_axes = snapshot.plate_position.columns

        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 5))
        painter.drawRect(x, y, width, height)
        for i, idx in enumerate(self.sensor_indexes):
            painter.setPen(QPen(self.sensor_colors[i], 5))
            solvent_idx, additive_idx = divmod(idx, 8)
            if snapshot.plate_position.direction == 0:
                sensor_x = x + column_axes[solvent_idx]
                sensor_y = y + row_axes[additive_idx]
            else:
                sensor_x = x + column_axes[additive_idx]
                sensor_y = y + row_axes[abs(solvent_idx - 11)]

            painter.drawEllipse(sensor_x - r, sensor_y - r, r * 2, r * 2)
        painter.end()

        return pixmap

    def on_refresh_clicked(self):
        self.lb.setText("NO CAMERA")
        self.camera_manager.connect_to_camera()

    def switch_view_mask(self):
        self.view_mask = not self.view_mask

        if self.view_mask:
            self.btn_view_mask.set_icon(self.img_view)
            self.btn_view_mask.setToolTip("마스킹 영역 숨기기")
        else:
            self.btn_view_mask.set_icon(self.img_view_hide)
            self.btn_view_mask.setToolTip("마스킹 영역 보이기")

    def open_mask_manager(self):
        if self.image is not None:
            mask_manager = MaskManagerController(snapshot=self.snapshot_instance)
            manager_view: MaskManagerView = mask_manager.view
            manager_view.on_select_changed(1)
            manager_view.view_radio.set_visibility(0, False)
            mask_manager.view.exec()

    def take_snapshot(self):
        if self.image is not None:
            snapshot: Snapshot = self.snapshot_instance
            snapshot.change_origin_image(Image(self.image))

    def set_sensor_indexes(self, indexes: list, colors: list):
        self.sensor_indexes = indexes
        self.sensor_colors = colors
        self.update_image(self.image)


class ImageViewerController(BaseController):
    capture_clicked = Signal()
    run_timeline_clicked = Signal(bool)
    instance_initialized = Signal()

    def __init__(self, parent=None, args: dict = None):
        if args is not None:
            self.mode = args.get("mode")
        else:
            self.mode = 0
        self.is_running_timeline = True

        super().__init__(ImageViewerModel, ImageViewerView, parent, args)

    def init_controller(self):
        super().init_controller()

        view: ImageViewerView = self.view
        view.btn_capture.clicked.connect(self.on_capture_clicked)
        view.instance_initialized.connect(self.instance_initialized.emit)
        self.on_capture_clicked()

    def on_capture_clicked(self):
        if self.mode == 0:
            self.capture_clicked.emit()
            return

        if self.mode == 1:
            self.switch_running_timeline(not self.is_running_timeline)

    def switch_running_timeline(self, run_timeline):
        self.is_running_timeline = run_timeline

        view: ImageViewerView = self.view
        if self.is_running_timeline:
            btn_text = "타임라인 촬영 중단"
        else:
            btn_text = "타임라인 촬영 시작"
        view.btn_capture.setText(btn_text)

        self.run_timeline_clicked.emit(self.is_running_timeline)

    def take_snapshot(self):
        view: ImageViewerView = self.view
        view.take_snapshot()

    def set_sensor_indexes(self, indexes: list, colors: list):
        view: ImageViewerView = self.view
        view.set_sensor_indexes(indexes, colors)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ImageViewerController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
