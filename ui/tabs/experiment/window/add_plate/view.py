import os
from datetime import datetime

from PySide6.QtGui import QFont, Qt, QIntValidator
from PySide6.QtWidgets import QLabel, QComboBox, QHBoxLayout, QWidget, QVBoxLayout, QLineEdit

from ui.common import BaseWidgetView, ImageButton, ColoredButton, ClickableLabel
from ui.common.date_picker import DatePicker
from util.setting_manager import SettingManager


class AddPlateView(BaseWidgetView):
    setting_manager = SettingManager()

    min_width = 250
    padding_title = 30
    width_box = 145
    width_calendar = 20
    width_date = 57
    width_time = 30
    width_confirm = 50
    height_et = 24

    metal_samples = []

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.setMinimumWidth(self.min_width)

        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        lb_title = QLabel("플레이트 추가")
        lb_title.setFont(font)
        lb_title.setStyleSheet(f"padding: {self.padding_title}px;")
        lyt_title = QHBoxLayout()
        lyt_title.addWidget(lb_title)
        lyt_title.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        lb_experiment = QLabel("실험")
        self.cmb_experiment = QComboBox()
        self.cmb_experiment.setFixedWidth(self.width_box)
        lyt_experiment = QHBoxLayout()
        lyt_experiment.addWidget(lb_experiment)
        lyt_experiment.addWidget(self.cmb_experiment)

        lb_combination = QLabel("조합")
        self.cmb_combination = QComboBox()
        self.cmb_combination.setFixedWidth(self.width_box)
        lyt_combination = QHBoxLayout()
        lyt_combination.addWidget(lb_combination)
        lyt_combination.addWidget(self.cmb_combination)

        lb_metal = QLabel("전이 금속")
        self.cmb_metal = QComboBox()
        self.cmb_metal.setFixedWidth(self.width_box)
        lyt_metal = QHBoxLayout()
        lyt_metal.addWidget(lb_metal)
        lyt_metal.addWidget(self.cmb_metal)

        """ 제작 일시 """
        lb_datetime = QLabel("제작 일시")

        """ 제작 일 라벨 및 캘린더 버튼 """
        now = datetime.now()
        date = now.strftime("%y%m%d")
        self.lb_date = ClickableLabel(date)
        self.lb_date.setFixedSize(self.width_date, self.height_et)
        self.lb_date.clicked.connect(self.open_date_picker)
        img_calendar = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    "../../../../../static/image/calendar.png")
        btn_date = ImageButton(image=img_calendar, size=(self.width_calendar, self.width_calendar))
        btn_date.clicked.connect(self.open_date_picker)
        wig_date = QWidget()
        wig_date.setObjectName("wig_date")
        wig_date.setFixedHeight(self.height_et)
        wig_date.setStyleSheet("#wig_date {border: 1px solid black;}")
        lyt_date = QHBoxLayout(wig_date)
        lyt_date.setContentsMargins(4, 0, 4, 0)
        lyt_date.addWidget(self.lb_date)
        lyt_date.addStretch()
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

        lb_note = QLabel("식별 문구")
        self.et_note = QLineEdit(self.setting_manager.get_experimenter_name())
        self.et_note.setFixedWidth(self.width_box)
        lyt_note = QHBoxLayout()
        lyt_note.addWidget(lb_note)
        lyt_note.addWidget(self.et_note)

        lb_name = QLabel("플레이트 명")
        self.lb_plate_name = QLabel("")
        self.lb_plate_name.setFixedWidth(self.width_box)
        lyt_name = QHBoxLayout()
        lyt_name.addWidget(lb_name)
        lyt_name.addWidget(self.lb_plate_name)

        lyt_form = QVBoxLayout()
        lyt_form.addStretch()
        lyt_form.addLayout(lyt_experiment)
        lyt_form.addLayout(lyt_combination)
        lyt_form.addLayout(lyt_metal)
        lyt_form.addLayout(lyt_datetime)
        lyt_form.addLayout(lyt_note)
        lyt_form.addLayout(lyt_name)
        lyt_form.addStretch()

        self.btn_confirm = ColoredButton("확인", padding="8px")
        self.btn_confirm.setFixedWidth(self.width_confirm)
        lyt_confirm = QHBoxLayout()
        lyt_confirm.addWidget(self.btn_confirm)
        lyt_confirm.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        lyt_confirm.setContentsMargins(self.padding_title, self.padding_title, self.padding_title, self.padding_title)

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_title)
        lyt.addLayout(lyt_form)
        lyt.addLayout(lyt_confirm)
        lyt.addStretch()

    def set_experiment_cmb_items(self, experiments):
        self.cmb_experiment.clear()
        if experiments:
            for experiment in experiments:
                self.cmb_experiment.addItem(experiment["name"])
        else:
            self.cmb_experiment.addItem("실험을 생성하세요.")

    def set_combination_cmb_items(self, combinations):
        self.cmb_combination.clear()
        if combinations:
            for combination in combinations:
                self.cmb_combination.addItem(combination["name"])
        else:
            self.cmb_combination.addItem("조합을 생성하세요.")

    def set_metal_cmb_items(self, metal_samples):
        self.metal_samples = metal_samples
        self.cmb_metal.clear()
        if metal_samples:
            for metal_sample in metal_samples:
                self.cmb_metal.addItem(metal_sample["name"])
        else:
            self.cmb_metal.addItem("금속을 추가하세요.")

    def set_date(self, date):
        date_string = date.toString("yyMMdd")
        self.lb_date.setText(date_string)
        self.set_plate_name()

    def open_date_picker(self):
        self.date_picker = DatePicker(self.set_date, self)
        self.date_picker.exec()

    def set_plate_name(self):
        metal_index = self.cmb_metal.currentIndex()
        if self.metal_samples:
            metal = self.metal_samples[metal_index]["metal"]["name"]
        else:
            metal = "metal"
        date = self.lb_date.text()
        note = self.et_note.text()

        note_str = f"_{note}" if note else ""
        plate_name = f"{metal}_{date}{note_str}"

        self.lb_plate_name.setText(plate_name)
