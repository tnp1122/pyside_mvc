from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QWidget, QHBoxLayout, QPushButton, QVBoxLayout

from ui.common import BaseScrollAreaView, BaseController
from ui.tabs.experiment.window.snapshot.capture.unit import PlateCaptureUnitController


class CaptureListModel:
    def __init__(self):
        pass


class CaptureListView(BaseScrollAreaView):
    unit_size = (300, 500)
    padding = 32

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.units = []
        self.selected_index = -1

    def closeEvent(self, event):
        for unit in self.units:
            unit.close()
        self.units = None

        self.btn_plus.close()
        self.widget.close()

        super().closeEvent(event)

    def init_view(self):
        super().init_view()

        font = QFont()
        font.setPointSize(96)
        font.setBold(True)

        self.btn_plus = QPushButton("+")
        self.btn_plus.setFont(font)
        self.btn_plus.clicked.connect(self.add_new_unit)
        lyt_plus = QVBoxLayout()
        lyt_plus.addWidget(self.btn_plus)
        lyt_plus.setAlignment(Qt.AlignTop)
        lyt_plus.setContentsMargins(0, 0, 0, 28)

        self.widget = QWidget()
        self.lyt = QHBoxLayout(self.widget)
        self.lyt.addLayout(lyt_plus)
        self.lyt.addStretch()
        self.lyt.setAlignment(Qt.AlignTop)

        self.set_unit_size(*self.unit_size)
        self.setWidget(self.widget)

    def set_unit_size(self, width=None, height=None):
        w = width if width else self.btn_plus.width()
        h = height if height else self.btn_plus.height()
        self.unit_size = (w, h)
        self.btn_plus.setFixedSize(w, h)
        for unit in self.units:
            unit.set_image_size(w, h)

        self.set_height()

    def add_new_unit(self):
        count = len(self.units)

        new_unit = PlateCaptureUnitController()
        new_unit.set_image_size(*self.unit_size)
        new_unit.view.clicked.connect(lambda: self.set_selected_widget(count))

        self.units.append(new_unit)
        self.set_selected_widget(count)
        self.lyt.insertWidget(count, new_unit.view)

    def set_height(self):
        scroll_bar_height = self.horizontalScrollBar().height()

        self.setFixedHeight(self.unit_size[1] + self.padding + scroll_bar_height)

    def set_selected_widget(self, selected_index):
        self.selected_index = selected_index
        for index, unit in enumerate(self.units):
            is_selected = index == selected_index
            unit.set_selected(is_selected)


class CaptureListController(BaseController):
    def __init__(self, parent=None):
        super().__init__(CaptureListModel, CaptureListView, parent)

    def init_controller(self):
        super().init_controller()

    def set_unit_size(self, width=None, height=None):
        w = width
        h = height
        view: CaptureListView = self.view
        view.set_unit_size(w, h)

    def set_unit_image(self, image):
        view: CaptureListView = self.view
        index = view.selected_index

        unit: PlateCaptureUnitController = view.units[index]
        unit.set_image(image)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = CaptureListController()
    widget.set_unit_size(300, 500)
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
