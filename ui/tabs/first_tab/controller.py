from PySide6.QtWidgets import QApplication

from ui.tabs.first_tab import FirstTabModel, FirstTabView


class FirstTabWidget:
    def __init__(self, parent=None):
        self._model = FirstTabModel()
        self._view = FirstTabView(parent)

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

    def set_current_index(self, index):
        self.view.setCurrentIndex(index.value)
        self.model.current_index = index

    def get_current_index(self):
        return self.model.current_index


def main():
    app = QApplication([])
    widget = FirstTabWidget()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
