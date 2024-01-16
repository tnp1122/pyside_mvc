from PySide6.QtWidgets import QVBoxLayout, QPushButton

from ui.common import BaseWidgetView
from ui.tabs.admin.user_list_table import UserListTableController


class AdminView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        lyt = QVBoxLayout(self)

        self.btn_get_waiting_users = QPushButton("조회")
        self.table_waiting_users = UserListTableController(self)

        lyt.addWidget(self.btn_get_waiting_users)
        lyt.addWidget(self.table_waiting_users.view)
