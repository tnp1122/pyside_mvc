from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QTabWidget

from ui.common import BaseWidgetView, ColoredButton
from ui.common.logo import Logo


class LoginView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.size_et = 110
        self.size_tabs = (220, 160)

    def init_ui(self):
        lyt = QVBoxLayout(self)

        lb_logo = Logo(with_title=True)
        tab_login = self.set_tab_login()
        tab_rg = self.set_tab_rg()

        tabs = QTabWidget()
        tabs.setFixedSize(*self.size_tabs)
        tabs.addTab(tab_login, "로그인")
        tabs.addTab(tab_rg, " 계정등록")

        lyt.addWidget(lb_logo, alignment=Qt.AlignHCenter)
        lyt.addStretch()
        lyt.addWidget(tabs, alignment=Qt.AlignHCenter)
        self.emit_ui_initialized_signal()

    def set_tab_login(self):
        tab = QWidget()
        lyt = QVBoxLayout(tab)

        lyt_username = QHBoxLayout()
        lb_username = QLabel("아이디")
        self.et_username_login = QLineEdit()
        self.et_username_login.setFixedWidth(self.size_et)
        lyt_username.addWidget(lb_username)
        lyt_username.addStretch()
        lyt_username.addWidget(self.et_username_login)

        lyt_password = QHBoxLayout()
        lb_password = QLabel("비밀번호")
        self.et_password_login = QLineEdit()
        self.et_password_login.setFixedWidth(self.size_et)
        lyt_password.addWidget(lb_password)
        lyt_password.addStretch()
        lyt_password.addWidget(self.et_password_login)

        self.btn_login = ColoredButton("로그인")

        # lyt.addStretch()
        lyt.addLayout(lyt_username)
        lyt.addLayout(lyt_password)
        lyt.addWidget(self.btn_login)
        lyt.addStretch()

        return tab

    def set_tab_rg(self):
        tab = QWidget()
        lyt = QVBoxLayout(tab)

        lyt_name = QHBoxLayout()
        lb_name = QLabel("이름")
        self.et_name = QLineEdit()
        self.et_name.setFixedWidth(self.size_et)
        lyt_name.addWidget(lb_name)
        lyt_name.addStretch()
        lyt_name.addWidget(self.et_name)

        lyt_username = QHBoxLayout()
        lb_username = QLabel("아이디")
        self.et_username_rg = QLineEdit()
        self.et_username_rg.setFixedWidth(self.size_et)
        lyt_username.addWidget(lb_username)
        lyt_username.addStretch()
        lyt_username.addWidget(self.et_username_rg)

        lyt_password = QHBoxLayout()
        lb_password = QLabel("비밀번호")
        self.et_password_rg = QLineEdit()
        self.et_password_rg.setFixedWidth(self.size_et)
        lyt_password.addWidget(lb_password)
        lyt_password.addStretch()
        lyt_password.addWidget(self.et_password_rg)

        self.btn_rg = ColoredButton("계정등록")

        # lyt.addStretch()
        lyt.addLayout(lyt_name)
        lyt.addLayout(lyt_username)
        lyt.addLayout(lyt_password)
        lyt.addWidget(self.btn_rg)
        lyt.addStretch()

        return tab
