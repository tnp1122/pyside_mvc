from PySide6.QtCore import Signal, QSize, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout

from ui.common import ColoredButton


class ConfirmationDialog(QDialog):
    confirmed = Signal()
    canceled = Signal()

    def __init__(
            self,
            title: str = "확인",
            content: str = "확인",
            confirm_text: str = "확인",
            cancel_text: str = "취소",
            use_confirm: bool = True,
            parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle(title)

        lb_content = QLabel(content)
        lb_content.setMinimumHeight(80)
        lb_content.setAlignment(Qt.AlignmentFlag.AlignTop)
        lb_content.setWordWrap(True)
        btn_cancel = ColoredButton(cancel_text, background_color="gray")
        btn_confirm = ColoredButton(confirm_text)

        btn_cancel.clicked.connect(self.cancel)
        btn_confirm.clicked.connect(self.confirm)

        lyt_btn = QHBoxLayout()
        lyt_btn.addWidget(btn_cancel)
        if use_confirm:
            lyt_btn.addWidget(btn_confirm)
        else:
            btn_cancel.set_background_color()

        lyt = QVBoxLayout(self)
        lyt.addWidget(lb_content)
        lyt.addStretch()
        lyt.addLayout(lyt_btn)

        self.setFixedSize(QSize(250, 150))

    def cancel(self):
        self.canceled.emit()
        self.close()

    def confirm(self):
        self.confirmed.emit()
        self.close()
