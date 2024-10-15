from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QWidget, QHBoxLayout

from models.snapshot import Snapshot
from ui.common import BaseScrollAreaView, BaseController
from ui.tabs.experiment.window.snapshot.mean_color.image_shell import ImageShell


class ImageListModel:
    def __init__(self):
        pass


class ImageListView(BaseScrollAreaView):
    image_size = (300, 520)
    padding = 64

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.image_shells = []
        self.set_height()

    def closeEvent(self, event):
        self.clear()

        super().closeEvent(event)

    def clear(self):
        for image_shell in self.image_shells:
            image_shell: ImageShell
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

    def add_new_shell(self, snapshot: Snapshot):
        count = len(self.image_shells)
        new_image_shell = ImageShell(snapshot)
        self.image_shells.append(new_image_shell)
        self.lyt.insertWidget(count, new_image_shell)

        self.set_height()

    def set_height(self):
        scroll_bar_height = self.horizontalScrollBar().height()

        self.setFixedHeight(self.image_size[1] + self.padding + scroll_bar_height)

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

    def add_new_shell(self, snapshot: Snapshot):
        view: ImageListView = self.view
        view.add_new_shell(snapshot)

    def set_use_lab_corrected_pixmap(self, use_lab_corrected_pixmap: bool):
        for image_shell in self.view.image_shells:
            image_shell: ImageShell
            snapshot: Snapshot = image_shell.snapshot
            snapshot.set_use_lab_corrected_pixmap(use_lab_corrected_pixmap)
            image_shell.set_image()

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
