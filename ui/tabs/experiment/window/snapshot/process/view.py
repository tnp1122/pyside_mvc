from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator, Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QLineEdit, QSizePolicy, QFrame

from ui.common import BaseWidgetView, ColoredButton, ImageButton, ClickableLabel
from ui.common.date_picker import DatePicker
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListController
from ui.tabs.experiment.window.snapshot.process.image_viewer import ImageViewerController

from util import image_converter as ic


class PlateProcessView(BaseWidgetView):
    plate_age_changed = Signal(int)

    width_box = 145
    width_calendar = 20
    width_date = 57
    width_time = 30
    height_et = 24

    def __init__(self, parent=None, snapshot_info=None):
        self.snapshot_info = snapshot_info
        self.captured_at = None
        self.plate_age = 0

        super().__init__(parent)

    def closeEvent(self, event):
        self.capture_list.close()

        super().closeEvent(event)

    def init_view(self):
        super().init_view()

        """ 촬영 일시 """
        lb_datetime = QLabel("촬영 일시")
        lb_datetime.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        """ 촬영 일 라벨 및 캘린더 버튼 """
        now = datetime.now()
        date = now.strftime("%y%m%d")
        self.lb_date = ClickableLabel(date)
        self.lb_date.setFixedSize(self.width_date, self.height_et)
        self.lb_date.clicked.connect(self.open_date_picker)
        img_calendar = ic.get_image_path("calendar.png")
        self.btn_date = ImageButton(image=img_calendar, size=(self.width_calendar, self.width_calendar))
        self.btn_date.clicked.connect(self.open_date_picker)
        self.wig_date = QWidget()
        self.wig_date.setObjectName("wig_date")
        self.wig_date.setFixedHeight(self.height_et)
        lyt_date = QHBoxLayout(self.wig_date)
        lyt_date.setContentsMargins(4, 0, 4, 0)
        lyt_date.addWidget(self.lb_date)
        lyt_date.addWidget(self.btn_date)

        """ 촬영 시간 입력 및 라벨 """
        validator = QIntValidator(0, 23)
        hour = "{:02d}".format(now.hour)
        self.et_time = QLineEdit(hour)
        self.et_time.setValidator(validator)
        self.et_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.et_time.setFixedSize(self.width_time, self.height_et)
        self.et_time.textChanged.connect(self.on_time_text_changed)
        lb_hour = QLabel("시")

        """ 촬영 시간 입력 박스 """
        wig_datetime_input = QWidget()
        wig_datetime_input.setFixedWidth(self.width_box)
        lyt_datetime_input = QHBoxLayout(wig_datetime_input)
        lyt_datetime_input.setContentsMargins(0, 0, 0, 0)
        lyt_datetime_input.addWidget(self.wig_date)
        lyt_datetime_input.addWidget(self.et_time)
        lyt_datetime_input.addWidget(lb_hour)
        lyt_datetime = QHBoxLayout()
        lyt_datetime.addWidget(lb_datetime)
        lyt_datetime.addWidget(wig_datetime_input)

        if self.snapshot_info["snapshot_id"]:
            self.set_et_editable(False)
        else:
            self.set_et_editable(True)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)

        lb_age = QLabel("플레이트 경과시간:")
        self.lb_snapshot_age = QLabel("")
        self.lb_snapshot_age.setFixedWidth(self.width_box)
        lyt_age = QHBoxLayout()
        lyt_age.addWidget(lb_age)
        lyt_age.addWidget(self.lb_snapshot_age)

        self.btn_save = ColoredButton("저장")

        lyt_top = QHBoxLayout()
        lyt_top.addLayout(lyt_datetime)
        lyt_top.addWidget(divider)
        lyt_top.addLayout(lyt_age)
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

        self.set_snapshot_age()

    def set_et_editable(self, editable=False):
        if editable:
            self.btn_date.setVisible(True)
            self.wig_date.setStyleSheet("#wig_date {border: 1px solid black;}")
            self.et_time.setStyleSheet("border: 1px solid black; padding: 4px;")
            self.et_time.setReadOnly(False)
        else:
            self.btn_date.setVisible(False)
            self.wig_date.setStyleSheet("#wig_date {border: 0px;}")
            self.et_time.setStyleSheet("border: 0px;")
            self.et_time.setReadOnly(True)

    def set_date(self, date):
        date_string = date.toString("yyMMdd")
        self.lb_date.setText(date_string)
        self.set_snapshot_age()

    def open_date_picker(self):
        self.date_picker = DatePicker(self.set_date, self)
        self.date_picker.exec()

    def on_time_text_changed(self, event):
        if int(event) <= 0:
            self.et_time.setText("0")

        elif int(event) > 23:
            self.et_time.setText("23")

        self.set_snapshot_age()

    def set_snapshot_age(self):
        plate_made_at_str = self.snapshot_info["plate_made_at"]
        plate_made_at = datetime.strptime(plate_made_at_str, "%Y-%m-%dT%H:%M:%S")

        captured_hour = self.et_time.text()
        captured_at_str = f"{self.lb_date.text()}_{captured_hour}"
        self.captured_at = datetime.strptime(captured_at_str, "%y%m%d_%H")

        time_diff = self.captured_at - plate_made_at
        self.plate_age = int(time_diff.total_seconds() / 3600)

        self.lb_snapshot_age.setText(f"{self.plate_age}H")

        self.plate_age_changed.emit(self.plate_age)
