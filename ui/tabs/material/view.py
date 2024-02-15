from ui.common import BaseTabWidgetView
from ui.tabs.material.tabs import MetalTabController, AdditiveTabController
from ui.tabs.material.tabs.solvent_tab import SolventTabController


class MaterialView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        # self.metal = MetalController()
        self.metal = MetalTabController()
        self.additive = AdditiveTabController()
        self.solvent = SolventTabController()

        self.setObjectName("material")
        self.tabBar().setObjectName("material_tabbar")

        background_color = "#5E6C80"

        style = f"""
            #material::pane {{
                background-color: {background_color};
                border: 6px solid {background_color};
            }}
            #material_tabbar::tab:selected {{
                background-color: {background_color};
                color: white;
            }}
        """
        child_style = f"""
            QTabBar::tab {{
                min-height: 10ex;
            }}
        """

        self.setStyleSheet(style)
        self.metal.view.setStyleSheet(child_style)
        self.additive.view.setStyleSheet(child_style)
        self.solvent.view.setStyleSheet(child_style)

        self.addTab(self.metal.view, "금속")
        self.addTab(self.additive.view, "첨가제")
        self.addTab(self.solvent.view, "용매")

