from ui.common.base_controller import BaseController
from ui.tabs.first_tab.setting import SettingModel, SettingView


class SettingController(BaseController):
    def __init__(self, parent=None):
        super().__init__(SettingModel, SettingView, parent)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = SettingController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
