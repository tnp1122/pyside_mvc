from PySide6.QtWidgets import QApplication

from ui.tabs.first_tab.setting import SettingModel, SettingView


class SettingWidget:
    def __init__(self, parent=None):
        self._model = SettingModel()
        self._view = SettingView(parent)

        self.view.ui_initialized_signal.connect(self.init_controller)
        self.view.init_ui()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def init_controller(self):
        pass


def main():
    app = QApplication([])
    widget = SettingWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
