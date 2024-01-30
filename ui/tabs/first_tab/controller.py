from ui.common import StackedWidgetController
from ui.tabs.first_tab import FirstTabModel, FirstTabView


class FirstTabController(StackedWidgetController):
    def __init__(self, parent=None):
        super().__init__(FirstTabModel, FirstTabView, parent)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = FirstTabController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
