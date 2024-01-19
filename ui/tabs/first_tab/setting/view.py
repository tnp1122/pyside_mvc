from PySide6.QtWidgets import QVBoxLayout, QPushButton

from ui.common import BaseWidgetView


class SettingView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        lyt = QVBoxLayout(self)

        self.btn = QPushButton("홈")
        self.btn_logout = QPushButton("로그아웃")

        lyt.addStretch()
        lyt.addWidget(self.btn)
        lyt.addWidget(self.btn_logout)
        lyt.addStretch()
