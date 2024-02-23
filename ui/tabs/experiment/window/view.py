from ui.common import BaseTabWidgetView


class ExperimentWindowView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
