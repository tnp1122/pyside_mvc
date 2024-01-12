from PySide6.QtWidgets import QVBoxLayout, QPushButton

from ui.common import BaseWidgetView
from ui.tabs.admin.user_list_table.controller import UserListTableWidget


class AdminView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        lyt = QVBoxLayout(self)

        self.btn_get_waiting_users = QPushButton("조회")
        self.table_waiting_users = UserListTableWidget(self)

        lyt.addWidget(self.btn_get_waiting_users)
        lyt.addWidget(self.table_waiting_users.view)

        self.emit_ui_initialized_signal()
