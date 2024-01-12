from PySide6.QtWidgets import QVBoxLayout

from ui.app.main_tab import MainTabWidget
from ui.app.info_bar import InfoBarWidget
from ui.common import BaseWidgetView


class AppView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.info_bar_margin = 2

    def showEvent(self, event):
        super().showEvent(event)
        self.update_info_bar_position()

    def init_ui(self):
        self.tabs = MainTabWidget(self)
        self.info_bar = InfoBarWidget(self)
        self.setMinimumSize(self.tabs.view.minimumSize())
        self.emit_ui_initialized_signal()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_info_bar_position()

    def update_info_bar_position(self):
        window_width, window_height = self.width(), self.height()

        x = window_width - self.info_bar.view.width() - self.info_bar_margin
        y = self.info_bar_margin

        self.tabs.view.setFixedSize(window_width, window_height)
        self.info_bar.view.move(x, y)
