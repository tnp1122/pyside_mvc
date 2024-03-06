from PySide6.QtWidgets import QLabel, QComboBox, QHBoxLayout, QVBoxLayout

from ui.common import BaseWidgetView, ColoredButton, MileStoneRadio
from ui.tabs.experiment.window.snapshot.difference.difference_table import ColorDifferenceTableController


class ColorDifferenceView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        lb_target = QLabel("Target")
        lb_control = QLabel("Control")
        self.cmb_target = QComboBox()
        self.cmb_control = QComboBox()
        self.btn_to_excel = ColoredButton("엑셀로 저장")

        lyt_top = QHBoxLayout()
        lyt_top.addWidget(lb_target)
        lyt_top.addWidget(self.cmb_target)
        lyt_top.addWidget(lb_control)
        lyt_top.addWidget(self.cmb_control)
        lyt_top.addStretch()
        lyt_top.addWidget(self.btn_to_excel)

        self.radio = MileStoneRadio(["RGB", "xyY", "Lab"])

        self.table = ColorDifferenceTableController()

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_top)
        lyt.addWidget(self.radio)
        lyt.addWidget(self.table.view, stretch=1)
        # lyt.addStretch()
