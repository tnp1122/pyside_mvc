from ui.common import BaseTabWidgetView
from util.colors import WHITE_GRAY


class ExperimentWindowView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)

    def set_style_sheet(self):
        self.setObjectName("ExperimentWindowTab")
        self.tabBar().setObjectName("ExperimentWindowTabBar")

        style = f"""
            #ExperimentWindowTab::pane {{
                background-color: lightgray;
                border: none;
        }}
            #ExperimentWindowTabBar::tab {{
                margin: 0px;
                padding: 5px 10px 5px 10px;
                background-color: {WHITE_GRAY};
                border-top: 1px solid lightgray;
                border-right: 1px solid lightgray;
        }}
            #ExperimentWindowTabBar::tab:first {{
                border-left: 1px solid lightgray;
        }}
            #ExperimentWindowTabBar::tab:selected {{
                background-color: lightgray;
        }}
        """

        self.setStyleSheet(style)
