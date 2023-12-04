from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QTabWidget


class HomeView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller

    def set_controller(self, controller):
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        lyt = QVBoxLayout(self)

        # 로그인 탭
        tab_login = QWidget()
        lyt_login = QVBoxLayout(tab_login)

        lyt_username_login = QHBoxLayout()
        lb_username_login = QLabel("아이디")
        self.et_username_login = QLineEdit()
        lyt_username_login.addWidget(lb_username_login)
        lyt_username_login.addWidget(self.et_username_login)

        lyt_password_login = QHBoxLayout()
        lb_password_login = QLabel("비밀번호")
        self.et_password_login = QLineEdit()
        lyt_password_login.addWidget(lb_password_login)
        lyt_password_login.addWidget(self.et_password_login)

        self.btn_login = QPushButton("로그인")

        lyt_login.addLayout(lyt_username_login)
        lyt_login.addLayout(lyt_password_login)
        lyt_login.addWidget(self.btn_login)

        # 계정등록 탭
        tab_rg = QWidget()
        lyt_rg = QVBoxLayout(tab_rg)

        lyt_name = QHBoxLayout()
        lb_name = QLabel("이름")
        self.et_name = QLineEdit()
        lyt_name.addWidget(lb_name)
        lyt_name.addWidget(self.et_name)

        lyt_username_rg = QHBoxLayout()
        lb_username_rg = QLabel("아이디")
        self.et_username_rg = QLineEdit()
        lyt_username_rg.addWidget(lb_username_rg)
        lyt_username_rg.addWidget(self.et_username_rg)

        lyt_password_rg = QHBoxLayout()
        lb_password_rg = QLabel("비밀번호")
        self.et_password_rg = QLineEdit()
        lyt_password_rg.addWidget(lb_password_rg)
        lyt_password_rg.addWidget(self.et_password_rg)

        self.btn_rg = QPushButton("계정등록")

        lyt_rg.addLayout(lyt_name)
        lyt_rg.addLayout(lyt_username_rg)
        lyt_rg.addLayout(lyt_password_rg)
        lyt_rg.addWidget(self.btn_rg)

        # 탭 연결
        tabs = QTabWidget()
        tabs.addTab(tab_login, "로그인")
        tabs.addTab(tab_rg, "계정등록")

        lyt.addWidget(tabs)

        # 시그널 연결
        self.et_username_login.textChanged.connect(self.controller.set_username_login)
        self.et_password_login.textChanged.connect(self.controller.set_password_login)
        self.et_username_rg.textChanged.connect(self.controller.set_username_rg)
        self.et_password_rg.textChanged.connect(self.controller.set_password_rg)
        self.et_name.textChanged.connect(self.controller.set_name)

        self.btn_login.clicked.connect(self.controller.do_login)
        self.btn_rg.clicked.connect(self.controller.do_registration)
