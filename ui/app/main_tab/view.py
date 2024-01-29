from PySide6.QtWidgets import QWidget

from ui.common import BaseTabWidgetView
from ui.tabs.admin import AdminController
from ui.tabs.experiment import ExperimentController
from ui.tabs.first_tab import FirstTabController


class MainTabView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.first = FirstTabController()
        self.experiment = ExperimentController()
        self.sample = QWidget()
        self.combination = QWidget()
        self.target = QWidget()
        self.data = QWidget()
        self.admin = AdminController()

        self.addTab(self.first.view, "메인")
        self.addTab(self.experiment.view, "실험")
        self.addTab(self.sample, "시료")
        self.addTab(self.combination, "조합")
        self.addTab(self.target, "타겟 물질")
        self.addTab(self.data, "데이터")

        self.setMinimumSize(640, 500)

    def set_admin_tab(self, visible=False):
        if visible:
            if self.count() == 6:
                self.addTab(self.admin.view, "관리자 화면")
        else:
            if self.count() == 7:
                self.removeTab(6)
