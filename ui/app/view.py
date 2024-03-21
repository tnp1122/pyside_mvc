from PySide6.QtGui import QIcon

from ui.app.main_tab import MainTabController
from ui.app.info_bar import InfoBarController
from ui.common.toast import Toast
from ui.common import BaseWidgetView

from util.camera_manager import CameraManager
from util import local_storage_manager as lsm


class AppView(BaseWidgetView):
    info_bar_margin = 2
    toast_margin = 20

    def __init__(self, parent=None):
        super().__init__(parent)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_floating_widget_position()

    def init_view(self):
        super().init_view()

        icon_path = lsm.get_static_image_path("pit_icon.ico")
        self.setWindowTitle("JEN-LiFE Pioneer kIT")
        self.setWindowIcon(QIcon(icon_path))

        self.toast = Toast(self)
        CameraManager(self)
        self.tabs = MainTabController(self)
        self.info_bar = InfoBarController(self)

        self.setMinimumSize(self.tabs.view.minimumSize())

        self.toast.raise_()
        self.toast.toasted_signal.connect(self.update_toast_position)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_floating_widget_position()

    def update_floating_widget_position(self):
        window_width, window_height = self.width(), self.height()

        info_x = window_width - self.info_bar.view.width() - self.info_bar_margin
        info_y = self.info_bar_margin

        self.tabs.view.setFixedSize(window_width, window_height)
        self.info_bar.view.move(info_x, info_y)

        self.update_toast_position()

    def update_toast_position(self):
        window_width, window_height = self.width(), self.height()
        toast_x = int((window_width - self.toast.width()) / 2)
        toast_y = window_height - self.toast_margin - self.toast.height()
        self.toast.move(toast_x, toast_y)
