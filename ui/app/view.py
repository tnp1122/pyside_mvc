from ui.app.main_tab import MainTabController
from ui.app.info_bar import InfoBarController
from ui.common import BaseWidgetView


class AppView(BaseWidgetView):
    info_bar_margin = 2

    def __init__(self, parent=None):
        super().__init__(parent)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_info_bar_position()

    def init_view(self):
        super().init_view()

        self.tabs = MainTabController(self)
        self.info_bar = InfoBarController(self)
        self.setMinimumSize(self.tabs.view.minimumSize())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_info_bar_position()

    def update_info_bar_position(self):
        window_width, window_height = self.width(), self.height()

        x = window_width - self.info_bar.view.width() - self.info_bar_margin
        y = self.info_bar_margin

        self.tabs.view.setFixedSize(window_width, window_height)
        self.info_bar.view.move(x, y)
