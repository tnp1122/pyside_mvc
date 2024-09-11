from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy

from ui.common.camera_widget.section_camera_display import SectionCameraDisplay
from ui.common.camera_widget.section_set_camera import SectionSetCamera


class CameraWidget(QWidget):
    def __init__(self, parent=None, use_mask=True, setting_visible=True, mask_border_visible=True):
        super().__init__(parent)

        self.setting_visible = setting_visible

        self.section_set_camera = SectionSetCamera()
        self.section_set_camera.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.camera_viewer = SectionCameraDisplay(
            use_mask=use_mask,
            setting_visible=setting_visible,
            mask_border_visible=mask_border_visible
        )

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self.section_set_camera)
        lyt.addWidget(self.camera_viewer)

        self.init_view()

    def init_view(self):
        self.section_set_camera.wb_roi_changed.connect(self.camera_viewer.update_wb_roi)
        self.section_set_camera.on_wb_roi_changed()

        self.camera_viewer.btn_switch_setting_visible.clicked.connect(
            lambda: self.switch_setting_visible(not self.setting_visible))

        self.switch_setting_visible(self.setting_visible)

    def switch_setting_visible(self, visible: bool = None):
        if visible is None:
            self.setting_visible = not self.setting_visible
        else:
            self.setting_visible = visible
        self.section_set_camera.setVisible(self.setting_visible)
        self.camera_viewer.switch_btn_setting_visible(self.setting_visible)

    def set_viewer_bottom_widget(self, widget: QWidget):
        self.camera_viewer.set_bottom_widget(widget)
