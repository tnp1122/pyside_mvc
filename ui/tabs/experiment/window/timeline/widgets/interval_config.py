from PySide6.QtCore import QSignalMapper, Signal
from PySide6.QtGui import QIntValidator, Qt
from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QDialog

from models.snapshot import RoundModel
from ui.common import ColoredButton


class IntervalConfig(QDialog):
    closed = Signal()

    def __init__(self, rounds: RoundModel, parent=None):
        super().__init__(parent)

        self.width_box = 60
        self.width_btn_add = 40
        self.width_btn_remove = 20
        self.width_lb_duration = 120
        self.rounds = rounds

        self.setWindowTitle("촬영 주기 설정")

        lb_interval = QLabel("촬영 주기")
        lb_count = QLabel("촬영 횟수")
        self.lb_duration = QLabel("촬영 기간")
        btn_add = ColoredButton("추가", padding="0px")
        btn_add.clicked.connect(self.on_add_btn)

        lb_interval.setAlignment(Qt.AlignCenter)
        lb_count.setAlignment(Qt.AlignCenter)
        self.lb_duration.setAlignment(Qt.AlignCenter)
        lb_interval.setFixedWidth(self.width_box)
        lb_count.setFixedWidth(self.width_box)
        self.lb_duration.setFixedWidth(self.width_box)
        btn_add.setFixedWidth(self.width_btn_add)

        lyt_header = QHBoxLayout()
        lyt_header.addWidget(lb_interval)
        lyt_header.addWidget(lb_count)
        lyt_header.addStretch()
        lyt_header.addWidget(self.lb_duration)
        lyt_header.addStretch()
        lyt_header.addWidget(btn_add)
        self.lyt_rows = QVBoxLayout()
        self.lyt_rows.setContentsMargins(0, 0, 0, 0)

        self.lyt = QVBoxLayout()
        self.lyt.addLayout(lyt_header)
        self.lyt.addLayout(self.lyt_rows)
        self.lyt.addStretch()
        self.lyt_container = QHBoxLayout(self)
        self.lyt_container.addStretch()
        self.lyt_container.addLayout(self.lyt)
        self.lyt_container.addStretch()

        self.mapper_text = QSignalMapper(self)
        self.mapper_text.mappedInt.connect(self.on_text_changed)
        self.mapper_btn_remove = QSignalMapper(self)
        self.mapper_btn_remove.mappedInt.connect(self.on_remove_btn)
        self.init_widget()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def clear_layout(self, layout):
        i = 0
        while layout.count():
            i += 1
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        layout.deleteLater()

    def init_widget(self):
        for index, round_data in enumerate(self.rounds):
            self.add_new_line(index, round_data)
        self.update_state()

    def add_new_line(self, row, round_data):
        rounds: RoundModel = self.rounds

        last_end = rounds.get_end_point(-1) if row != 0 else 0
        new_end = rounds.get_end_point()
        duration_str = f"{last_end}초~{new_end}초"

        et_interval = QLineEdit(str(round_data["interval"]))
        et_count = QLineEdit(str(round_data["count"]))
        lb_duration = QLabel(duration_str)
        btn_remove = QPushButton("x")
        container_remove = QWidget()
        container_remove.setFixedWidth(self.width_btn_add)
        lyt_container_remove = QHBoxLayout(container_remove)
        lyt_container_remove.setContentsMargins(0, 0, 0, 0)
        lyt_container_remove.addWidget(btn_remove)

        validator = QIntValidator(1, 999999)
        et_interval.setValidator(validator)
        et_count.setValidator(validator)

        et_interval.setFixedWidth(self.width_box)
        et_count.setFixedWidth(self.width_box)
        btn_remove.setFixedWidth(self.width_btn_remove)

        et_interval.textChanged.connect(self.mapper_text.map)
        et_count.textChanged.connect(self.mapper_text.map)
        btn_remove.clicked.connect(self.mapper_btn_remove.map)
        self.mapper_text.setMapping(et_interval, row)
        self.mapper_text.setMapping(et_count, row)
        self.mapper_btn_remove.setMapping(btn_remove, row)

        lyt_round = QHBoxLayout()
        lyt_round.addWidget(et_interval)
        lyt_round.addWidget(et_count)
        lyt_round.addStretch()
        lyt_round.addWidget(lb_duration)
        lyt_round.addStretch()
        lyt_round.addWidget(container_remove)

        self.lyt_rows.addLayout(lyt_round)

    def get_lyt_round(self, index) -> QHBoxLayout:
        return self.lyt_rows.itemAt(index)

    def update_state(self):
        rounds: RoundModel = self.rounds
        first_btn_remove = None
        for index in range(self.lyt_rows.count()):
            last_end = rounds.get_end_point(index - 1) if index != 0 else 0
            new_end = rounds.get_end_point(index)
            duration_str = f"{'{:,.0f}'.format(last_end)}초~{'{:,.0f}'.format(new_end)}초"

            lyt_round = self.get_lyt_round(index)
            btn_remove = lyt_round.itemAt(5).widget().layout().itemAt(0).widget()
            if index == 0:
                first_btn_remove = btn_remove
            btn_remove.setVisible(True)

            lb_duration: QLabel = lyt_round.itemAt(3).widget()
            lb_duration.setText(duration_str)
        if len(self.rounds) == 1 and first_btn_remove is not None:
            first_btn_remove.setVisible(False)

        self.adjustSize()
        self.setFixedSize(self.lyt_container.sizeHint())

    def add_round(self):
        rounds: RoundModel = self.rounds
        round_data = rounds.add_round()

        self.add_new_line(len(rounds) - 1, round_data)

    def on_text_changed(self, index):
        lyt_round = self.get_lyt_round(index)
        et_interval: QLineEdit = lyt_round.itemAt(0).widget()
        et_count: QLineEdit = lyt_round.itemAt(1).widget()

        interval_val = int(et_interval.text())
        count_val = int(et_count.text())
        rounds: RoundModel = self.rounds
        if 0 < interval_val != rounds[index]["interval"]:
            rounds.set_interval(index, interval_val)

        if 0 < count_val != rounds[index]["count"]:
            rounds.set_count(index, count_val)

        self.update_state()

    def on_add_btn(self):
        self.add_round()
        self.update_state()

    def on_remove_btn(self, row):
        lyt_round = self.get_lyt_round(row)
        rounds: RoundModel = self.rounds
        rounds.remove_round(row)
        self.clear_layout(lyt_round)
        self.lyt_rows.removeItem(lyt_round)
        self.update_state()

        if row == self.lyt_rows.count():
            return

        for row in range(row, self.lyt_rows.count()):
            lyt_round = self.get_lyt_round(row)
            btn_remove = lyt_round.itemAt(5).widget().layout().itemAt(0).widget()
            self.mapper_text.removeMappings(lyt_round.itemAt(0).widget())
            self.mapper_text.removeMappings(lyt_round.itemAt(1).widget())
            self.mapper_btn_remove.removeMappings(btn_remove)

            self.mapper_text.setMapping(lyt_round.itemAt(0).widget(), row)
            self.mapper_text.setMapping(lyt_round.itemAt(1).widget(), row)
            self.mapper_btn_remove.setMapping(btn_remove, row)
