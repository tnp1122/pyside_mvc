from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QSizePolicy

from admin.user_list_table import UserListTable


class AdminView(QWidget):
    ui_initialized_signal = Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller

    def set_controller(self, controller):
        print("admidView: set_controller")
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        print("admidView: init_ui")
        lyt = QVBoxLayout(self)

        self.btn = QPushButton("조회")
        self.table = UserListTable(self)

        lyt.addWidget(self.btn)
        lyt.addWidget(self.table.get_view())

        self.btn.clicked.connect(self.controller.get_user_list)

        self.ui_initialized_signal.emit()

    def set_table_items(self, user_list):
        self.controller.set_table_items(user_list)
