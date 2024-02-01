import os

from PySide6.QtWidgets import QVBoxLayout, QComboBox, QHBoxLayout

from ui.common import BaseWidgetView, ColoredButton, ImageButton
from ui.tabs.target_material.target_list_table import TargetListTableController


class TargetMaterialView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        img_refresh = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  "../../../static/image/refresh.png")
        self.cb = QComboBox()
        self.btn_refresh = ImageButton(image=img_refresh)
        self.btn_cancle = ColoredButton("취소", background_color="gray")
        self.btn_save = ColoredButton("저장", background_color="red")

        lyt_top = QHBoxLayout()
        lyt_top.addWidget(self.cb)
        lyt_top.addWidget(self.btn_refresh)
        lyt_top.addStretch()
        lyt_top.addWidget(self.btn_cancle)
        lyt_top.addWidget(self.btn_save)

        self.target_list_table = TargetListTableController()

        lyt = QVBoxLayout(self)
        lyt.addLayout(lyt_top)
        lyt.addWidget(self.target_list_table.view)

    def set_combo_box_items(self, experiments):
        self.cb.clear()
        for experiment in experiments:
            self.cb.addItem(experiment["name"])

    def set_target_list_table_items(self, target_list):
        self.target_list_table.set_table_items(target_list)
