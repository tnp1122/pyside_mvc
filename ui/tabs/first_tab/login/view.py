from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QTabWidget

from ui.common import BaseWidgetView, ColoredButton, Logo


class LoginView(BaseWidgetView):
    enter_pressed_signal = Signal(int)
    size_et = 110
    size_tabs = (220, 180)

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            self.enter_pressed_signal.emit(self.tabs.currentIndex())

    def init_view(self):
        super().init_view()

        lyt = QVBoxLayout(self)

        lb_logo = Logo(with_title=True)
        tab_login = self.set_tab_login()
        tab_rg = self.set_tab_rg()

        self.tabs = QTabWidget()
        self.tabs.setFixedSize(*self.size_tabs)
        self.tabs.addTab(tab_login, "로그인")
        self.tabs.addTab(tab_rg, "실험자 등록")
        tabs_style_sheet = f"""
            QTabWidget::pane {{ border: 0px; }}
            QTabBar::tab {{ min-width: {(self.tabs.width()-2) // self.tabs.count()}px; border:0px; }}
            QTabBar::tab:first {{ border-right: 2px solid black; }}
            QTabBar::tab:selected {{ color: black; font-weight: bold; }}
            QTabBar::tab:!selected {{ color: #818181; font-weight: normal; }}
        """
        self.tabs.setStyleSheet(tabs_style_sheet)

        lyt.addWidget(lb_logo, alignment=Qt.AlignHCenter)
        lyt.addStretch()
        lyt.addWidget(self.tabs, alignment=Qt.AlignHCenter)
        lyt.addStretch()

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
        self.et_password_login.setEchoMode(QLineEdit.Password)
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
        self.et_password_rg.setEchoMode(QLineEdit.Password)
        lyt_password.addWidget(lb_password)
        lyt_password.addStretch()
        lyt_password.addWidget(self.et_password_rg)

        lyt_confirm_password = QHBoxLayout()
        lb_confirm_password = QLabel("비밀번호 확인")
        self.et_confirm_password = QLineEdit()
        self.et_confirm_password.setFixedWidth(self.size_et)
        self.et_confirm_password.setEchoMode(QLineEdit.Password)
        lyt_confirm_password.addWidget(lb_confirm_password)
        lyt_confirm_password.addStretch()
        lyt_confirm_password.addWidget(self.et_confirm_password)

        self.btn_rg = ColoredButton("실험자 등록")

        # lyt.addStretch()
        lyt.addLayout(lyt_name)
        lyt.addLayout(lyt_username)
        lyt.addLayout(lyt_password)
        lyt.addLayout(lyt_confirm_password)
        lyt.addWidget(self.btn_rg)
        lyt.addStretch()

        return tab
