import os

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel

from ui.common import BaseWidgetView, ImageButton


class InfoBarView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        lyt = QHBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)

        self.lb_name = QLabel("사용자")
        font = self.lb_name.font()
        font.setUnderline(True)
        self.lb_name.setFont(font)
        self.lb_name_after = QLabel("님")

        image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../../static/image/cogwheel.png")
        cogwheel = QPixmap(image_path)
        self.btn_setting = ImageButton(image=cogwheel)

        lyt.addStretch()
        lyt.addWidget(self.lb_name)
        lyt.addWidget(self.lb_name_after)
        lyt.addWidget(self.btn_setting)
        lyt.addStretch()

