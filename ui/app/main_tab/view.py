from PySide6.QtWidgets import QWidget

from ui.common import BaseTabWidgetView
from ui.tabs.admin import AdminPage
from ui.tabs.first_tab import FirstTabWidget


class MainTabView(BaseTabWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        self.first = FirstTabWidget()
        self.experiment = QWidget()
        self.sample = QWidget()
        self.combination = QWidget()
        self.target = QWidget()
        self.data = QWidget()
        self.admin = AdminPage()

        self.addTab(self.first.view, "메인")
        self.addTab(self.experiment, "실험")
        self.addTab(self.sample, "시료")
        self.addTab(self.combination, "조합")
        self.addTab(self.target, "타겟 물질")
        self.addTab(self.data, "데이터")
        self.addTab(self.admin.view, "관리자 화면")

        self.setMinimumSize(640, 500)
        self.emit_ui_initialized_signal()
