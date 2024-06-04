from ui.common import StackedWidgetController
from ui.tabs.first_tab.setting import SettingModel, SettingView
from ui.tabs.first_tab.setting.camera import SettingCameraView
from util.enums import SettingViewIndex


class SettingController(StackedWidgetController):
    def __init__(self, parent=None):
        super().__init__(SettingModel, SettingView, parent)

        view: SettingView = self.view
        view.btn_set_camera.clicked.connect(self.show_set_camera_widget)

    def show_set_camera_widget(self):
        view: SettingView = self.view

        view.show_set_camera_widget()
        set_camera_view: SettingCameraView = view.widget_set_camera.view
        set_camera_view.btn_back.clicked.connect(self.on_close_set_camera_widget)
        self.set_current_index(SettingViewIndex.CAMERA)

    def on_close_set_camera_widget(self):
        view: SettingView = self.view

        self.set_current_index(SettingViewIndex.CAMERA)
        view.on_close_set_camera_widget()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = SettingController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
