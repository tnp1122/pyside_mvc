from ui.common import BaseTabWidgetView


class ExperimentWindowView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)

        self.tabCloseRequested.connect(self.close_tab)

    def init_view(self):
        super().init_view()

    def close_tab(self, index):
        self.removeTab(index)
