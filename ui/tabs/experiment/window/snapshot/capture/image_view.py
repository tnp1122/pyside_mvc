from ui.common import BaseWidgetView, BaseController


class ImageViewerModel:
    def __init__(self):
        pass


class ImageViewerView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()


class ImageViewerController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ImageViewerModel, ImageViewerView, parent)

    def init_controller(self):
        super().init_controller()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ImageViewerController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
