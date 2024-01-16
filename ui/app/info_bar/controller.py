from ui.app.info_bar import InfoBarModel, InfoBarView
from ui.common import BaseController


class InfoBarController(BaseController):
    def __init__(self, parent=None):
        super().__init__(InfoBarModel, InfoBarView, parent)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = InfoBarController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
