import os

from PySide6.QtWidgets import QVBoxLayout, QComboBox, QHBoxLayout

from ui.common import BaseWidgetView, ColoredButton, ImageButton
from ui.tabs.target_material.target_table import TargetTableController


class TargetMaterialView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        img_refresh = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  "../../../static/image/refresh.png")
        self.cmb = QComboBox()
        self.btn_refresh = ImageButton(image=img_refresh)
        self.btn_cancle = ColoredButton("취소", background_color="gray")
        self.btn_save = ColoredButton("저장", background_color="red")

        lyt_top = QHBoxLayout()
        lyt_top.addWidget(self.cmb)
        lyt_top.addWidget(self.btn_refresh)
        lyt_top.addStretch()
        lyt_top.addWidget(self.btn_cancle)
        lyt_top.addWidget(self.btn_save)

        self.tb_target = TargetTableController()

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_top)
        lyt.addWidget(self.tb_target.view)

    def set_experiment_cmb_items(self, experiments):
        self.cmb.clear()
        for experiment in experiments:
            self.cmb.addItem(experiment["name"])

    def set_target_table_items(self, targets):
        self.tb_target.set_table_items(targets)
