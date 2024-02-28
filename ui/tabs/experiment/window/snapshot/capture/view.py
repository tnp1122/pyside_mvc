import os
from datetime import datetime

from PySide6.QtGui import QIntValidator, Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QLineEdit, QSizePolicy

from ui.common import BaseWidgetView, ColoredButton, ImageButton, ClickableLabel
from ui.common.date_picker import DatePicker
from ui.tabs.experiment.window.snapshot.capture.capture_list import CaptureListController
from ui.tabs.experiment.window.snapshot.capture.image_viewer import ImageViewerController


class PlateCaptureView(BaseWidgetView):
    width_box = 145
    width_calendar = 20
    width_date = 57
    width_time = 30
    height_et = 24

    def __init__(self, parent=None):
        super().__init__(parent)

    def closeEvent(self, event):
        self.capture_list.close()

        super().closeEvent(event)

    def init_view(self):
        super().init_view()

        """ 제작 일시 """
        lb_datetime = QLabel("제작 일시")
        lb_datetime.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        """ 제작 일 라벨 및 캘린더 버튼 """
        now = datetime.now()
        date = now.strftime("%y%m%d")
        self.lb_date = ClickableLabel(date)
        self.lb_date.setFixedSize(self.width_date, self.height_et)
        self.lb_date.clicked.connect(self.open_date_picker)
        img_calendar = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    "../../../../../../static/image/calendar.png")
        btn_date = ImageButton(image=img_calendar, size=(self.width_calendar, self.width_calendar))
        btn_date.clicked.connect(self.open_date_picker)
        wig_date = QWidget()
        wig_date.setObjectName("wig_date")
        wig_date.setFixedHeight(self.height_et)
        wig_date.setStyleSheet("#wig_date {border: 1px solid black;}")
        lyt_date = QHBoxLayout(wig_date)
        lyt_date.setContentsMargins(4, 0, 4, 0)
        lyt_date.addWidget(self.lb_date)
        lyt_date.addWidget(btn_date)

        """ 제작 시간 입력 및 라벨 """
        validator = QIntValidator(0, 23)
        hour = "{:02d}".format(now.hour)
        self.et_time = QLineEdit(hour)
        self.et_time.setValidator(validator)
        self.et_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.et_time.setStyleSheet("border: 1px solid black; padding: 4px;")
        self.et_time.setFixedSize(self.width_time, self.height_et)
        lb_hour = QLabel("시")

        """ 제작 시간 입력 박스 """
        wig_datetime_input = QWidget()
        wig_datetime_input.setFixedWidth(self.width_box)
        lyt_datetime_input = QHBoxLayout(wig_datetime_input)
        lyt_datetime_input.setContentsMargins(0, 0, 0, 0)
        lyt_datetime_input.addWidget(wig_date)
        lyt_datetime_input.addWidget(self.et_time)
        lyt_datetime_input.addWidget(lb_hour)
        lyt_datetime = QHBoxLayout()
        lyt_datetime.addWidget(lb_datetime)
        lyt_datetime.addWidget(wig_datetime_input)

        self.btn_save = ColoredButton("저장")

        lyt_top = QHBoxLayout()
        lyt_top.addLayout(lyt_datetime)
        lyt_top.addStretch()
        lyt_top.addWidget(self.btn_save)

        self.image_viewer = ImageViewerController()

        self.capture_list = CaptureListController()
        self.capture_list.set_unit_size(300, 500)

        lyt_content = QHBoxLayout()
        lyt_content.addWidget(self.image_viewer.view)
        lyt_content.addWidget(self.capture_list.view)

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_top)
        lyt.addStretch()
        lyt.addLayout(lyt_content)
        lyt.addStretch()

    def set_date(self, date):
        date_string = date.toString("yyMMdd")
        self.lb_date.setText(date_string)
        # self.set_snapshot_name()

    def open_date_picker(self):
        self.date_picker = DatePicker(self.set_date, self)
        self.date_picker.exec()
