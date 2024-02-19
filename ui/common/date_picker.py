from PySide6.QtWidgets import QDialog, QCalendarWidget, QHBoxLayout, QVBoxLayout

from ui.common import ColoredButton


class DatePicker(QDialog):
    def __init__(self, callback, parent=None):
        super().__init__()
        self.setWindowTitle("제작 날짜")
        self.callback = callback

        btn_cancel = ColoredButton("취소", background_color="gray")
        btn_confirm = ColoredButton("확인", background_color="red")
        btn_cancel.clicked.connect(self.on_cancel)
        btn_confirm.clicked.connect(self.on_confirm)
        self.calendar = QCalendarWidget()

        lyt_btn = QHBoxLayout()
        lyt_btn.addStretch()
        lyt_btn.addWidget(btn_cancel)
        lyt_btn.addWidget(btn_confirm)
        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_btn)
        lyt.addWidget(self.calendar)

    def on_cancel(self):
        self.close()

    def on_confirm(self):
        date = self.calendar.selectedDate()
        self.callback(date)
        self.close()
