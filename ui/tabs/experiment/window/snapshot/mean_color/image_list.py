from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QWidget, QHBoxLayout

from ui.common import BaseScrollAreaView, BaseController
from ui.tabs.experiment.window.snapshot.mean_color.image_shell import ImageShell


class ImageListModel:
    def __init__(self):
        pass


class ImageListView(BaseScrollAreaView):
    image_size = (300, 500)
    padding = 32

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.image_shells = []

    def closeEvent(self, event):
        self.clear()

        super().closeEvent(event)

    def clear(self):
        for image_shell in self.image_shells:
            self.lyt.removeWidget(image_shell)
            image_shell.close()

        self.image_shells = []

    def init_view(self):
        super().init_view()

        self.widget = QWidget()
        self.lyt = QHBoxLayout(self.widget)
        self.lyt.addStretch()
        self.lyt.setAlignment(Qt.AlignTop)

        self.setWidget(self.widget)

    def set_height(self):
        scroll_bar_height = self.horizontalScrollBar().height()

        self.setFixedHeight(self.image_size[1] + self.padding + scroll_bar_height)

    def set_image_size(self, width=None, height=None):
        w = width if width else self.image_size[0]
        h = height if height else self.image_size[1]
        self.image_size = (w, h)

        for image_shell in self.image_shells:
            image_shell.set_image_size(w, h)

        self.set_height()

    def set_image_shell(self, index, mean_colored_pixmap, cropped_original_pixmap, target_name):
        shell: ImageShell = self.image_shells[index]
        shell.set_image_shell(mean_colored_pixmap, cropped_original_pixmap, target_name)

    def add_image_shell(self):
        count = len(self.image_shells)
        new_image_shell = ImageShell()
        new_image_shell.set_image_size(*self.image_size)
        self.image_shells.append(new_image_shell)
        self.lyt.insertWidget(count, new_image_shell)

    def set_image_type(self, index):
        for image_shell in self.image_shells:
            image_shell: ImageShell
            image_shell.set_current_image_type(index)


class ImageListController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ImageListModel, ImageListView, parent)

    def init_controller(self):
        super().init_controller()

    def clear(self):
        view: ImageListView = self.view
        view.clear()

    def set_image_size(self, width=None, height=None):
        view: ImageListView = self.view
        view.set_image_size(width, height)

    def set_image_type(self, index):
        view: ImageListView = self.view
        view.set_image_type(index)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ImageListController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
