from PySide6.QtCore import QSignalMapper, Signal
from PySide6.QtWidgets import QTableWidgetItem, QPushButton, QSizePolicy, QHBoxLayout, QWidget, QHeaderView

from ui.common import BaseTableWidgetView


class UserListTableView(BaseTableWidgetView):
    approved_signal = Signal(int)
    rejected_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        self.setMinimumWidth(400)
        self.setColumnCount(4)

        headers = ["이름", "아이디", "요청일자", "승인"]
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.emit_ui_initialized_signal()

    def clear_table(self):
        for row in range(self.rowCount()):
            item = self.cellWidget(row, 3)
            if item:
                item.deleteLater()
        self.setRowCount(0)

    def set_table_items(self, user_list):
        print("user_list:", user_list)
        self.clear_table()
        self.mapper_approve = QSignalMapper(self)
        self.mapper_reject = QSignalMapper(self)
        self.mapper_approve.mappedInt.connect(self.on_approve_clicked)
        self.mapper_reject.mappedInt.connect(self.on_reject_clicked)

        for row, user in enumerate(user_list):
            print(f"user_index: {row}, user: {user}")
            self.insertRow(row)
            # print("user:", user)
            name = QTableWidgetItem(user["name"])
            username = QTableWidgetItem(user["username"])
            regist_date = user["regist_date"]
            approve_buttons = self.get_approve_buttons(row)

            print(regist_date)
            regist_date = QTableWidgetItem(user["regist_date"].split("T")[0])
            self.setItem(row, 0, name)
            self.setItem(row, 1, username)
            self.setItem(row, 2, regist_date)
            self.setCellWidget(row, 3, approve_buttons)

        self.resizeRowsToContents()
        self.resizeColumnToContents(3)

    def get_approve_buttons(self, row):
        btn_approve = QPushButton("승인")
        btn_reject = QPushButton("거절")
        self._adjust_button_size(btn_approve)
        self._adjust_button_size(btn_reject)
        btn_approve.clicked.connect(self.mapper_approve.map)
        btn_reject.clicked.connect(self.mapper_reject.map)
        self.mapper_approve.setMapping(btn_approve, row)
        self.mapper_reject.setMapping(btn_reject, row)

        lyt_approve = QHBoxLayout()
        lyt_approve.addWidget(btn_approve)
        lyt_approve.addWidget(btn_reject)
        lyt_approve.setContentsMargins(0, 0, 0, 0)
        lyt_approve.setSpacing(5)

        container_approve = QWidget()
        container_approve.setLayout(lyt_approve)

        return container_approve

    def _adjust_button_size(self, button):
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setStyleSheet("QPushButton { text-align: center; padding: 5px; }")

    def on_approve_clicked(self, row):
        self.approved_signal.emit(row)

    def on_reject_clicked(self, row):
        self.rejected_signal.emit(row)
