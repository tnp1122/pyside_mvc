from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy

from ui.common import SetCamera
from ui.common.camera_widget.camera_viewer import CameraViewer


class CameraWidget(QWidget):
    def __init__(self, parent=None, setting_visible=True):
        super().__init__(parent)

        self.setting_visible = setting_visible

        self.set_camera = SetCamera()
        self.set_camera.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.camera_viewer = CameraViewer(setting_visible=self.setting_visible)

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self.set_camera)
        lyt.addWidget(self.camera_viewer)

        self.init_view()

    def init_view(self):
        self.set_camera.wb_roi_changed.connect(self.camera_viewer.update_wb_roi)
        self.set_camera.on_wb_roi_changed()

        self.camera_viewer.btn_switch_setting_visible.clicked.connect(
            lambda: self.switch_setting_visible(not self.setting_visible))

        self.switch_setting_visible(self.setting_visible)

    def switch_setting_visible(self, visible: bool = None):
        if visible is None:
            self.setting_visible = not self.setting_visible
        else:
            self.setting_visible = visible
        self.set_camera.setVisible(self.setting_visible)
        self.camera_viewer.switch_btn_setting_visible(self.setting_visible)

    def set_viewer_bottom_widget(self, widget: QWidget):
        self.camera_viewer.set_bottom_widget(widget)
