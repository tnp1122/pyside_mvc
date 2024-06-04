from ui.common import BaseController
from ui.tabs.first_tab.setting.camera import SettingCameraModel, SettingCameraView


class SettingCameraController(BaseController):
    def __init__(self, parent=None):
        super().__init__(SettingCameraModel, SettingCameraView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = SettingCameraController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
