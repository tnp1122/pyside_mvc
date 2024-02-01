from PySide6.QtCore import QObject


class BaseController(QObject):
    def __init__(self, Model, View, parent=None, args=None):
        super().__init__()
        self._model = Model()
        if args:
            self._view = View(parent, args)
        else:
            self._view = View(parent)
        self.view._late_init.signal.connect(self.late_init)
        self.init_controller()
        self.on_controller_initialized()

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    def init_controller(self):
        self.init_view()
        self.on_view_initialized()

        # print(f"parent init controller")

    def late_init(self):
        pass

    def init_view(self):
        self.view.init_view()

    def on_view_initialized(self):
        self.view.on_view_initialized()
        # print("부모 ui 초기화 후")
        pass

    def on_controller_initialized(self):
        # print("부모 컨트롤러 초기화 후")
        pass


class StackedWidgetController(BaseController):
    def __init__(self, Model, View, parent=None, args=None):
        super().__init__(Model, View, parent, args)

    def set_current_index(self, index):
        self.view.setCurrentIndex(index.value)
        self.model.current_index = index

    def get_current_index(self):
        return self.model.current_index


class TableWidgetController(BaseController):
    table_items = None

    def __init__(self, Model, View, parent=None, args=None):
        super().__init__(Model, View, parent, args)

    def set_table_items(self, items):
        self.table_items = items
        self.view.set_table_items(items)

    def cancel_added_items(self):
        self.set_table_items(self.table_items)

    def get_new_items(self):
        origin_count = len(self.table_items)
        new_table_items = []

        for row in range(origin_count + 1, self.view.rowCount()):
            new_table_items.append(self.view.item(row, 0).text())

        return new_table_items
