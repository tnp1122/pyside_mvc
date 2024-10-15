from PySide6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy

from ui.common.camera_widget.camera_widget_status import CameraWidgetStatus
from ui.common.camera_widget.section_camera_display import SectionCameraDisplay
from ui.common.camera_widget.section_set_camera import SectionSetCamera


class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.status = CameraWidgetStatus(None)
        self.snapshot_instance = self.status.snapshot_instance

        self.section_set_camera = SectionSetCamera(self.status)
        self.section_set_camera.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.camera_display = SectionCameraDisplay(self.status)

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self.section_set_camera)
        lyt.addWidget(self.camera_display)

        self.init_view()

    def init_view(self):
        self.section_set_camera.wb_roi_changed.connect(self.camera_display.update_wb_roi)
        self.section_set_camera.on_wb_roi_changed()
        self.section_set_camera.gbox_wb.toggled.connect(self.on_gbox_wb_toggled)

        self.camera_display.btn_switch_setting_visible.clicked.connect(self.on_btn_switch_setting_visible_clicked)

        self.update_setting_visible()

    def update_setting_visible(self):
        visible = self.status.setting_visible
        self.section_set_camera.setVisible(visible)
        self.camera_display.update_setting_visible()

    def on_gbox_wb_toggled(self, is_opened):
        self.status.set_wb_roi_visible(is_opened)

    def on_btn_switch_setting_visible_clicked(self):
        self.status.switch_setting_visible()
        self.update_setting_visible()

    def set_viewer_bottom_widget(self, widget: QWidget):
        self.camera_display.set_bottom_widget(widget)
