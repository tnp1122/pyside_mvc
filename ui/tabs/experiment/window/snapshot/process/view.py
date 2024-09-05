from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, QFrame, QPushButton

from ui.common import BaseWidgetView, ColoredButton
from ui.common.camera_widget import CameraWidget
from ui.common.date_picker import DateWidget, HourWidget
from ui.tabs.experiment.window.snapshot.process.capture_list import CaptureListController


class SnapshotProcessView(BaseWidgetView):
    snapshot_age_changed = Signal(int)

    width_box = 145
    width_calendar = 20
    width_date = 57
    width_time = 30
    height_et = 24

    def __init__(self, parent=None, snapshot_info=None):
        self.snapshot_info = snapshot_info
        self.captured_at = datetime.strptime(snapshot_info["snapshot_captured_at"], "%Y-%m-%dT%H:%M:%S")
        self.snapshot_age = 0

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
        lb_size = (self.width_date, self.height_et)
        calendar_size = (self.width_calendar, self.width_calendar)
        self.wig_date = DateWidget(self.captured_at, lb_size, calendar_size)
        self.wig_date.set_callback(self.set_snapshot_age)

        """ 촬영 시간 입력 및 라벨 """
        et_size = (self.width_time, self.height_et)
        self.wig_hour = HourWidget(self.captured_at, et_size)
        self.wig_hour.et.textChanged.connect(self.set_snapshot_age)

        """ 촬영 시간 입력 박스 """
        wig_datetime_input = QWidget()
        wig_datetime_input.setFixedWidth(self.width_box)
        lyt_datetime_input = QHBoxLayout(wig_datetime_input)
        lyt_datetime_input.setContentsMargins(0, 0, 0, 0)
        lyt_datetime_input.addWidget(self.wig_date)
        lyt_datetime_input.addWidget(self.wig_hour)
        lyt_datetime = QHBoxLayout()
        lyt_datetime.addWidget(lb_datetime)
        lyt_datetime.addWidget(wig_datetime_input)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)

        lb_age = QLabel("플레이트 경과시간:")
        self.lb_snapshot_age = QLabel("")
        self.lb_snapshot_age.setFixedWidth(self.width_box)
        lyt_age = QHBoxLayout()
        lyt_age.addWidget(lb_age)
        lyt_age.addWidget(self.lb_snapshot_age)

        self.btn_init_mask = ColoredButton("마스크 초기화", background_color="gray")
        self.btn_apply_mask = ColoredButton("마스크 일괄 적용", color="black", background_color="white")
        self.btn_save = ColoredButton("저장")

        lyt_top = QHBoxLayout()
        lyt_top.addLayout(lyt_datetime)
        lyt_top.addWidget(divider)
        lyt_top.addLayout(lyt_age)
        lyt_top.addStretch()
        lyt_top.addWidget(self.btn_init_mask)
        lyt_top.addWidget(self.btn_apply_mask)
        lyt_top.addWidget(self.btn_save)

        self.btn_capture = ColoredButton("촬영")
        self.camera_widget = CameraWidget(use_mask=False, setting_visible=False, mask_area_visible=False)
        self.camera_widget.set_viewer_bottom_widget(self.btn_capture)

        self.capture_list = CaptureListController()
        self.capture_list.set_unit_size(300, 500)
        self.btn_init_mask.clicked.connect(self.capture_list.init_plate_mask_info)
        self.btn_apply_mask.clicked.connect(self.capture_list.apply_plate_mask_info)

        lyt_content = QHBoxLayout()
        lyt_content.addWidget(self.camera_widget)
        lyt_content.addWidget(self.capture_list.view)

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_top)
        lyt.addLayout(lyt_content)

        self.set_snapshot_age()

        if self.snapshot_info["snapshot_id"]:
            self.set_editable(False)
        else:
            self.set_editable(True)

    def set_editable(self, editable=False):
        self.wig_date.set_editable(editable)
        self.wig_hour.set_editable(editable)
        self.btn_save.setVisible(editable)

    def set_snapshot_age(self):
        plate_made_at_str = self.snapshot_info["plate_made_at"]
        plate_made_at = datetime.strptime(plate_made_at_str, "%Y-%m-%dT%H:%M:%S")

        captured_hour = self.wig_hour.et.text()
        captured_at_str = f"{self.wig_date.lb.text()}_{captured_hour}"
        self.captured_at = datetime.strptime(captured_at_str, "%y%m%d_%H")

        time_diff = self.captured_at - plate_made_at
        self.snapshot_age = int(time_diff.total_seconds() / 3600)

        self.lb_snapshot_age.setText(f"{self.snapshot_age}H")

        self.snapshot_age_changed.emit(self.snapshot_age)
