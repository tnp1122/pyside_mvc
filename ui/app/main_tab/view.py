from ui.common import BaseTabWidgetView
from ui.tabs.first_tab import FirstTabWidget


class MainTabView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        self.first_tab = FirstTabWidget()
        self.addTab(self.first_tab.view, "메인")

        self.setMinimumSize(640, 500)
        self.emit_ui_initialized_signal()
