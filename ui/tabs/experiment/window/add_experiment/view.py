from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QLineEdit

from ui.common import BaseWidgetView, ColoredButton


class AddExperimentView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        lyt = QVBoxLayout(self)

        lb = QLabel("실험 추가")
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        lb.setFont(font)

        lyt_name = QHBoxLayout()
        lb_name = QLabel("실험명")
        self.et_name = QLineEdit()

        lyt_name.addWidget(lb_name)
        lyt_name.addWidget(self.et_name)

        self.btn_add = ColoredButton("확인")

        lyt.addStretch()
        lyt.addWidget(lb)
        lyt.addLayout(lyt_name)
        lyt.addWidget(self.btn_add)
        lyt.addStretch()

        self.setMaximumSize(300, 300)
        lyt.setAlignment(lb, Qt.AlignCenter)
