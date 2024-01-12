from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from ui.common import BaseStackedWidgetView
from ui.tabs.first_tab.home import HomeWidget
from ui.tabs.first_tab.login import LoginWidget
from ui.tabs.first_tab.setting import SettingWidget
from util.enums import FirstTabIndex


class FirstTabView(BaseStackedWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        self.login = LoginWidget()
        self.home = HomeWidget()
        self.setting = SettingWidget()

        num_widgets = len(FirstTabIndex)
        for index in range(num_widgets):
            if FirstTabIndex(index) == FirstTabIndex.LOGIN:
                self.addWidget(self.with_container(self.login.view))
            elif FirstTabIndex(index) == FirstTabIndex.HOME:
                self.addWidget(self.with_container(self.home.view))
            elif FirstTabIndex(index) == FirstTabIndex.SETTING:
                self.addWidget(self.with_container(self.setting.view))

        self.emit_ui_initialized_signal()

    def with_container(self, widget):
        container = QWidget(self)
        lyt = QVBoxLayout(container)
        lyt.addWidget(widget, alignment=Qt.AlignVCenter | Qt.AlignHCenter)

        return container