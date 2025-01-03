from ui.common import BaseStackedWidgetView
from ui.tabs.first_tab.home import HomeController
from ui.tabs.first_tab.login import LoginWidget
from ui.tabs.first_tab.setting import SettingController
from util.enums import FirstTabIndex


class FirstTabView(BaseStackedWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        self.login = LoginWidget()
        self.home = HomeController()
        self.setting = SettingController()

        num_widgets = len(FirstTabIndex)
        for index in range(num_widgets):
            if FirstTabIndex(index) == FirstTabIndex.LOGIN:
                self.addWidget(self.with_container(self.login.view))
            elif FirstTabIndex(index) == FirstTabIndex.HOME:
                self.addWidget(self.with_container(self.home.view))
            elif FirstTabIndex(index) == FirstTabIndex.SETTING:
                self.addWidget(self.setting.view)
