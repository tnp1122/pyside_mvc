from PySide6.QtGui import QIcon

from ui.app.info_bar import InfoBarController
from ui.app.main_tab import MainTabController
from ui.common import BaseWidgetView
from ui.common.loading_spinner import LoadingSpinner
from ui.common.toast import Toast
from util import local_storage_manager as lsm
from util.camera_manager import CameraManager, CameraUnit


class AppView(BaseWidgetView):
    info_bar_margin = 2
    toast_margin = 20

    def __init__(self, parent=None):
        super().__init__(parent)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_floating_widget_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_floating_widget_position()

    def init_view(self):
        super().init_view()

        icon_path = lsm.get_static_image_path("pit_icon.ico")
        self.setWindowTitle("JEN-LiFE Pioneer kIT")
        self.setWindowIcon(QIcon(icon_path))

        self.tabs = MainTabController(self)
        self.info_bar = InfoBarController(self)

        self.setMinimumSize(self.tabs.view.minimumSize())

        self.toast = Toast(self)
        CameraManager(self)

        self.loading_spinner = LoadingSpinner(self)
        self.loading_spinner.raise_()
        self.toast.raise_()
        self.toast.toasted_signal.connect(self.update_toast_position)

    def set_style_sheet(self):
        self.setObjectName("App")
        style = f"""
            #App {{
                background-color: white;
            }}
        """
        self.setStyleSheet(style)

    def update_floating_widget_position(self):
        window_width, window_height = self.width(), self.height()

        info_x = window_width - self.info_bar.view.width() - self.info_bar_margin
        info_y = self.info_bar_margin

        self.tabs.view.setFixedSize(window_width, window_height)
        self.info_bar.view.move(info_x, info_y)

        self.update_toast_position()
        self.update_loading_spinner_position(window_width, window_height)

    def update_toast_position(self):
        window_width, window_height = self.width(), self.height()
        toast_x = int((window_width - self.toast.width()) / 2)
        toast_y = window_height - self.toast_margin - self.toast.height()
        self.toast.move(toast_x, toast_y)

    def update_loading_spinner_position(self, window_width, window_height):
        self.loading_spinner.setFixedWidth(window_width)
        self.loading_spinner.setFixedSize(window_width, window_height)
        self.loading_spinner.move(0, 30)

    def closeEvent(self, event):
        CameraUnit().close_camera()
