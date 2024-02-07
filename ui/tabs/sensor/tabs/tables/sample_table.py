import os
from datetime import datetime

from PySide6.QtCore import Signal, QSignalMapper, Qt
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QPushButton, QComboBox, \
    QLabel, QCalendarWidget, QVBoxLayout

from ui.common import BaseTableWidgetView, ImageButton, TableWidgetController, ColoredButton
from util.setting_manager import SettingManager


class SampleTableModel:
    def __init__(self):
        pass


class SampleTableView(BaseTableWidgetView):
    setting_manager = SettingManager()
    change_use_signal = Signal(int)

    samples = []
    subjects = []
    not_use_samples = set()

    def __init__(self, parent=None, args=None):
        super().__init__(parent)

        self.subject = args["tables"]
        self.headers = args["headers"]
        self.is_metal = self.subject == "metal"

    def init_view(self):
        super().init_view()

        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.not_use_samples = self.get_not_use_samples()

    def get_not_use_samples(self):
        if self.is_metal:
            return self.setting_manager.get_not_use_metal_samples()
        return self.setting_manager.get_not_use_additive_samples()

    def set_not_use_samples(self, samples):
        if self.is_metal:
            self.setting_manager.set_not_use_metal_samples(samples)
        else:
            self.setting_manager.set_not_use_additive_samples(samples)

    def set_table_items(self, items):
        self.clear_table()
        self.samples = items

        self.mapper_change_use = QSignalMapper(self)
        self.mapper_change_use.mappedInt.connect(self.on_change_use)

        for row, item in enumerate(items):
            sample_id = item["id"]
            dt_obj = datetime.strptime(item["made_at"], "%Y-%m-%dT%H:%M:%S")

            self.insertRow(row)
            name = QTableWidgetItem(item["name"])
            subject = QTableWidgetItem(item[self.subject]["name"])
            made_at = QTableWidgetItem(dt_obj.strftime("%Y-%m-%d"))

            cb_use = QCheckBox()
            if sample_id not in self.not_use_samples:
                cb_use.setChecked(True)
            cb_use.stateChanged.connect(self.mapper_change_use.map)
            self.mapper_change_use.setMapping(cb_use, row)
            widget_cb_use = QWidget()
            lyt_cb_use = QHBoxLayout(widget_cb_use)
            lyt_cb_use.addWidget(cb_use)
            lyt_cb_use.setAlignment(Qt.AlignCenter)
            lyt_cb_use.setContentsMargins(0, 0, 0, 0)

            self.setItem(row, 0, name)
            self.setItem(row, 1, subject)
            self.setItem(row, 2, made_at)
            self.setCellWidget(row, 3, widget_cb_use)
            self.set_editable(name, False)
            self.set_editable(subject, False)
            self.set_editable(made_at, False)

        count = self.rowCount()
        self.insertRow(count)
        self.setSpan(count, 0, 1, self.horizontalHeader().length())

        btn = QPushButton("추가")
        btn.clicked.connect(self.add_new_row)
        self._adjust_button_size(btn)

        container = QWidget()
        lyt_btn = QHBoxLayout(container)
        lyt_btn.addWidget(btn)
        lyt_btn.setContentsMargins(0, 0, 0, 0)
        lyt_btn.setSpacing(5)

        self.setCellWidget(count, 0, container)

    def add_new_row(self):
        count = self.rowCount()
        super().add_new_row()

        def set_date_(date):
            self.set_date(date, count)

        def open_date_picker():
            self.date_picker = DatePicker(set_date_, self)
            self.date_picker.show()

        current_date = datetime.now().strftime("%Y-%m-%d")
        img_calendar = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    "../../../../../static/image/calendar.png")

        cmb_subject = QComboBox()
        widget_date = QWidget()
        lyt_date = QHBoxLayout(widget_date)
        lb_date = QLabel(current_date)
        btn_date = ImageButton(image=img_calendar, size=(18, 18))

        btn_date.clicked.connect(open_date_picker)
        lyt_date.addWidget(lb_date)
        lyt_date.addStretch()
        lyt_date.addWidget(btn_date)
        lyt_date.setContentsMargins(0, 0, 0, 0)

        self.setCellWidget(count, 1, cmb_subject)
        self.setCellWidget(count, 2, widget_date)
        self.set_subjects(count)

    def update_subjects(self, subjects):
        self.subjects = subjects
        self.set_subjects()

    def set_subjects(self, row=None):
        sample_count = len(self.samples)
        row_count = self.rowCount()

        def set_combo_box(row_=None):
            cmb_subject = self.cellWidget(row_, 1)
            if cmb_subject is not None and isinstance(cmb_subject, QComboBox):
                cmb_subject.clear()
                for subject in self.subjects:
                    cmb_subject.addItem(subject["name"])

        if row:
            set_combo_box(row)
            return

        for row in range(sample_count, row_count):
            set_combo_box(row)

    def set_date(self, date, row):
        date_str = date.toString("yyyy-MM-dd")
        widget = self.cellWidget(row, 2)
        lyt = widget.layout()
        lb_date = lyt.itemAt(0).widget()
        lb_date.setText(date_str)

    def on_change_use(self, row):
        subject_id = self.samples[row]["id"]

        widget_check = self.cellWidget(row, 3)
        lyt_check = widget_check.layout()
        is_checked = lyt_check.itemAt(0).widget().isChecked()

        if is_checked:
            if subject_id in self.not_use_samples:
                self.not_use_samples.remove(subject_id)
        else:
            self.not_use_samples.add(subject_id)

        self.set_not_use_samples(self.not_use_samples)


class SampleTableController(TableWidgetController):
    def __init__(self, parent=None, args=None):
        super().__init__(SampleTableModel, SampleTableView, parent, args)

    def init_controller(self):
        super().init_controller()

    def get_new_items(self):
        origin_count = len(self.table_items)
        new_table_items = []

        for row in range(origin_count + 1, self.view.rowCount()):
            sample = {}
            made_at_str = self.view.cellWidget(row, 2).layout().itemAt(0).widget().text()
            made_at = made_at_str + "T00:00:00"

            sample["name"] = self.view.item(row, 0).text()
            sample[self.view.subject] = self.view.cellWidget(row, 1).currentText()
            sample["made_at"] = made_at
            if sample["name"].strip():
                new_table_items.append(sample)

        return new_table_items

    def update_subject(self, subject_items):
        self.view.update_subjects(subject_items)


class DatePicker(QWidget):
    def __init__(self, set_date, parent=None):
        super().__init__()
        self.setWindowTitle("제작 날짜")
        self.set_date = set_date

        btn_cancel = ColoredButton("취소", background_color="gray")
        btn_confirm = ColoredButton("확인", background_color="red")
        btn_confirm.clicked.connect(self.on_confirm)
        self.calendar = QCalendarWidget()

        lyt_btn = QHBoxLayout()
        lyt_btn.addStretch()
        lyt_btn.addWidget(btn_cancel)
        lyt_btn.addWidget(btn_confirm)
        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_btn)
        lyt.addWidget(self.calendar)

    def on_confirm(self):
        date = self.calendar.selectedDate()
        self.set_date(date)
        self.close()
