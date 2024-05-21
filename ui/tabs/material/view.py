from util.colors import PRIMARY
from ui.common import BaseTabWidgetView
from ui.tabs.material.tabs import MetalTabController, AdditiveTabController
from ui.tabs.material.tabs.solvent_tab import SolventTabController


class MaterialView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.metal = MetalTabController()
        self.additive = AdditiveTabController()
        self.solvent = SolventTabController()

        self.addTab(self.metal.view, "금속")
        self.addTab(self.additive.view, "첨가제")
        self.addTab(self.solvent.view, "용매")

    def set_style_sheet(self):
        self.setObjectName("MaterialTab")
        self.tabBar().setObjectName("MaterialTabBar")

        style = f"""
            #MaterialTab::pane {{
                background-color: {PRIMARY};
                border: 6px solid {PRIMARY};
            }}
            #MaterialTabBar::tab {{
                margin: 0px;
                padding: 5px 10px 5px 10px;
                background-color: white;
                border: 0.5px solid {PRIMARY};
            }}
            #MaterialTabBar::tab:selected {{
                background-color: {PRIMARY};
                border-color: {PRIMARY};
                color: white;
            }}
        """

        child_style = f"""
            QTabWidget::pane {{
                padding: 0px;
                border: none;
            }}
            QTabBar::tab {{
                min-height: 6ex;
                padding: 5px 10px 5px 10px;
                background-color: lightgray;
                border: none;
            }}
            QTabBar::tab:selected {{
                background-color: white;
            }}
        """

        self.setStyleSheet(style)
        self.metal.view.setStyleSheet(child_style)
        self.additive.view.setStyleSheet(child_style)
        self.solvent.view.setStyleSheet(child_style)
