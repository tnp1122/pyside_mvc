from PySide6.QtCore import QObject


class BaseController(QObject):
    def __init__(self, Model, View, parent=None):
        super().__init__()
        self._model = Model()
        self._view = View(parent)
        self.init_controller()
        self.on_controller_initialized()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def init_controller(self):
        self.view.init_view()
        self.on_view_initialized()

        # print(f"parent init controller")

    def on_view_initialized(self):
        self.view.on_view_initialized()
        # print("부모 ui 초기화 후")
        pass

    def on_controller_initialized(self):
        # print("부모 컨트롤러 초기화 후")
        pass
