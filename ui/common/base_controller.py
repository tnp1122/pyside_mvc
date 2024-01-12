from PySide6.QtCore import QObject, Signal


class BaseController(QObject):
    controller_initialized_signal = Signal()

    def __init__(self, Model, View, parent=None):
        super().__init__()
        self._model = Model()
        self._view = View(parent)
        self.view.ui_initialized_signal.connect(self.init_controller)

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def init_controller(self):
        pass
