from PySide6.QtCore import Signal, QSignalMapper
from PySide6.QtWidgets import QWidget, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton

from ui.common import BaseWidgetView, ColoredButton, RefreshButton
from ui.tabs.combination.widgets import LabelTitle, Cell, SelectSensorWidget, Label


class CombinationView(BaseWidgetView):
    cell_clicked_signal = Signal(str)
    box_width = 140

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.cmb_experiment = QComboBox()
        self.cmb_experiment.setMinimumWidth(self.box_width)
        self.cmb_combination = QComboBox()
        self.cmb_combination.setFixedWidth(self.box_width)
        self.btn_refresh = RefreshButton()
        self.et_combination_name = QLineEdit("새 조합")
        self.et_combination_name.setFixedWidth(self.box_width)
        self.btn_new_combination = ColoredButton("새 조합 만들기")
        self.btn_cancel = ColoredButton("취소", background_color="gray")
        self.btn_save = ColoredButton("저장", background_color="red")

        widget_tob_bar = QWidget()
        lyt_tob_bar = QHBoxLayout(widget_tob_bar)
        lyt_tob_bar.setContentsMargins(0, 0, 0, 0)
        lyt_tob_bar.addWidget(self.cmb_experiment)
        lyt_tob_bar.addWidget(self.cmb_combination)
        lyt_tob_bar.addWidget(self.btn_refresh)
        lyt_tob_bar.addWidget(self.et_combination_name)
        lyt_tob_bar.addStretch()
        lyt_tob_bar.addWidget(self.btn_cancel)
        lyt_tob_bar.addWidget(self.btn_save)
        lyt_tob_bar.addWidget(self.btn_new_combination)

        self.mapper_clicked = QSignalMapper(self)
        self.mapper_clicked.mappedString.connect(lambda index: self.cell_clicked_signal.emit(index))
        self.lyt_grid = QGridLayout()
        self.init_grid()

        lyt = QVBoxLayout(self)
        lyt.addWidget(widget_tob_bar)
        lyt.addStretch()
        lyt.addLayout(self.lyt_grid)
        lyt.addStretch()

        self.select_sensor_widget = SelectSensorWidget()

    def add_new_combination(self):
        pass

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

    def init_grid(self):
        label_title = LabelTitle()
        self.lyt_grid.addWidget(label_title, 12, 0)

        for x in range(8):
            lb = Label(x, False)
            self.add_to_grid(lb, x+1, 12)

        for y in range(12):
            lb = Label(12 - y)
            self.add_to_grid(lb, 0, y)

        for x in range(1, 9):
            for y in range(12):
                index = (11 - y) * 8 + x - 1
                cell = Cell(index)
                self.add_to_grid(cell, x, y)

        for i in range(1, self.lyt_grid.columnCount()):
            self.lyt_grid.setColumnStretch(i, 1)

    def clear_grid(self):
        for x in range(1, 9):
            for y in range(12):
                widget = self.lyt_grid.itemAtPosition(11 - y, x)
                if widget:
                    widget.widget().set_solvent()
                    widget.widget().set_additive()

    def set_grid_items(self, associations):
        self.clear_grid()
        for association in associations:
            y, x = divmod(association["idx"], 8)

            widget = self.lyt_grid.itemAtPosition(11 - y, x + 1)
            if widget:
                sensor = association["sensor"]
                widget.widget().set_solvent(sensor["solvent"])
                widget.widget().set_additive(sensor["additive"])

    def add_to_grid(self, widget: QPushButton, x, y):
        self.lyt_grid.addWidget(widget, y, x)
        widget.clicked.connect(self.mapper_clicked.map)
        self.mapper_clicked.setMapping(widget, f"{x}, {y}")

    # def get_cell(self, x, y):
    #     cell = Cell()
    #     cell.clicked.connect(self.mapper_clicked.map)
    #     self.mapper_clicked.setMapping(cell, f"{x}, {y}")
    #
    #     return cell

    def switch_cell_style(self, editable: bool):
        for column in range(1, 9):
            for row in range(12):
                widget = self.lyt_grid.itemAtPosition(11 - row, column)
                if widget:
                    widget.widget().switch_style(editable)
