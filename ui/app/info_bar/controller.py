from PySide6.QtWidgets import QApplication

from ui.app.info_bar import InfoBarModel, InfoBarView


class InfoBarWidget:
    def __init__(self, parent=None):
        self._model = InfoBarModel()
        self._view = InfoBarView(parent)

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
    widget = InfoBarWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
