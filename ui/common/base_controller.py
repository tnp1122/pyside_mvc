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


class BaseControllerV2:
    def __init__(self, Model, View, parent=None):
        super().__init__()
        self._model = Model()
        self._view = View(parent)
        self.init_controller()
        self.on_controller_initialiezd()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def init_controller(self):
        self.view.init_view()
        self.on_ui_initialized()

        # print(f"parent init controller")

    def on_ui_initialized(self):
        # print("부모 ui 초기화 후")
        pass

    def on_controller_initialiezd(self):
        # print("부모 컨트롤러 초기화 후")
        pass
