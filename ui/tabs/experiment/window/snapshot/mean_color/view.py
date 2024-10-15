from PySide6.QtWidgets import QVBoxLayout, QCheckBox

from ui.common import BaseWidgetView, MileStoneRadio
from ui.tabs.experiment.window.snapshot.mean_color.image_list import ImageListController


class MeanColorView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.cb_apply_lab_correct = QCheckBox("Lab 보정 적용")
        self.cb_apply_lab_correct.setEnabled(False)
        self.radio = MileStoneRadio(["평균 색", "실제 색"])
        self.image_list = ImageListController()

        lyt = QVBoxLayout(self)
        lyt.addWidget(self.cb_apply_lab_correct)
        lyt.addWidget(self.radio)
        lyt.addStretch()
        lyt.addWidget(self.image_list.view)
        lyt.addStretch()

    def init_view(self):
        super().init_view()

        self.cb_apply_lab_correct.stateChanged.connect(self.on_cb_apply_lab_correct_changed)
        self.radio.selected.connect(self.on_radio_selected)

    def on_cb_apply_lab_correct_changed(self):
        use_lab_corrected_pixmap = self.cb_apply_lab_correct.isChecked()
        self.image_list.set_use_lab_corrected_pixmap(use_lab_corrected_pixmap)

    def on_radio_selected(self, index):
        self.image_list.set_image_type(index)
