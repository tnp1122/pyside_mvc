import math
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog, QCalendarWidget, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QLineEdit, QComboBox

from ui.common import ImageButton, ClickableLabel
from util import local_storage_manager as lsm


class DatePicker(QDialog):
    def __init__(self, callback, parent=None):
        from ui.common import ColoredButton

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


class DateWidget(QWidget):
    changed = Signal(datetime)

    def __init__(
            self,
            now: datetime = datetime.now(),
            lb_size: tuple = (57, 24),
            btn_size: tuple = (20, 20),
            parent: QWidget = None
    ):
        super().__init__(parent)
        # 랩핑 오류 때문에 스타일 시트를 명시적으로 활성화해야함
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("wig_date")

        date = now.strftime("%y%m%d")
        img_calendar = lsm.get_static_image_path("calendar.png")

        self.lb = ClickableLabel(date)
        self.lb.setFixedSize(*lb_size)
        self.btn = ImageButton(image=img_calendar, size=btn_size)

        self.setFixedHeight(lb_size[1])
        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(4, 0, 4, 0)
        lyt.addWidget(self.lb)
        lyt.addStretch()
        lyt.addWidget(self.btn)

        self.set_editable()
        self.set_callback(init=True)

    def set_callback(self, callback=None, init=False):
        def new_handler(date):
            self.on_date_picked(date)
            if callback is not None and callable(callback):
                callback()

        if not init:
            self.lb.label_clicked.disconnect()
            self.btn.clicked.disconnect()
        self.lb.label_clicked.connect(lambda: self.open_date_picker(new_handler))
        self.btn.clicked.connect(lambda: self.open_date_picker(new_handler))

    def on_date_picked(self, date):
        date_string = date.toString("yyMMdd")
        self.lb.setText(date_string)
        self.changed.emit(datetime.strptime(date_string, "%y%m%d"))

    def open_date_picker(self, callback):
        if self.editable:
            self.date_picker = DatePicker(callback, self)
            self.date_picker.exec()

    def set_editable(self, editable=True):
        self.editable = editable
        if editable:
            self.btn.setVisible(True)
            self.setStyleSheet("#wig_date {border: 1px solid black;}")
        else:
            self.btn.setVisible(False)
            self.setStyleSheet("#wig_date {border: 0px;}")


class HourWidget(QWidget):
    changed = Signal(int)

    def __init__(
            self,
            now: datetime = datetime.now(),
            et_size: tuple = (30, 24),
            parent=None
    ):
        super().__init__(parent)

        validator = QIntValidator(0, 23)
        hour = "{:02d}".format(now.hour)

        self.et = QLineEdit(hour)
        self.et.setValidator(validator)
        self.et.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.et.setFixedSize(*et_size)
        self.et.textChanged.connect(self.on_time_text_changed)
        lb_hour = QLabel("시")

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self.et)
        lyt.addWidget(lb_hour)

    def on_time_text_changed(self, event):
        if int(event) < 0:
            self.et.setText("0")
        elif int(event) > 23:
            self.et.setText("23")

        self.changed.emit(int(self.et.text()))

    def set_editable(self, editable=True):
        self.editable = editable
        if editable:
            self.et.setStyleSheet("border: 1px solid black; padding: 4px;")
            self.et.setReadOnly(False)
        else:
            self.et.setStyleSheet("border: 0px;")
            self.et.setReadOnly(True)

    @property
    def hour(self):
        return int(self.et.text())


class HourDropWidget(QWidget):
    changed = Signal(int)

    def __init__(
            self,
            now: datetime = datetime.now(),
            cmb_size: tuple = (42, 24),
            parent=None
    ):
        super().__init__(parent)

        hours = [str(i) for i in range(24)]
        index = hours.index(str(now.hour))

        self.cmb = QComboBox()
        self.cmb.setFixedSize(*cmb_size)
        self.cmb.addItems(hours)
        self.cmb.setCurrentIndex(index)
        self.cmb.currentIndexChanged.connect(self.on_cmb_changed)

        lb = QLabel("시")

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self.cmb)
        lyt.addWidget(lb)

    @property
    def hour(self):
        return int(self.cmb.currentText())

    def on_cmb_changed(self):
        self.changed.emit(self.hour)


class MinuteWidget(QWidget):
    changed = Signal(int)

    def __init__(
            self,
            now: datetime = datetime.now(),
            interval: int = 10,
            cmb_size: tuple = (42, 24),
            parent=None
    ):
        super().__init__(parent)

        minutes = [str(i * interval) for i in range(60 // interval)]
        minute = math.ceil(now.minute / interval) * interval
        if minute == 60:
            minute = 0

        index = minutes.index(str(minute))
        self.cmb = QComboBox()
        self.cmb.setFixedSize(*cmb_size)
        self.cmb.addItems(minutes)
        self.cmb.setCurrentIndex(index)
        self.cmb.currentIndexChanged.connect(self.on_cmb_changed)

        lb = QLabel("분")

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self.cmb)
        lyt.addWidget(lb)

    @property
    def minute(self):
        return int(self.cmb.currentText())

    def on_cmb_changed(self):
        self.changed.emit(self.minute)
