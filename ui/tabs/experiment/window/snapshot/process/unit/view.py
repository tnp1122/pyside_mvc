import os

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, Qt, QFont
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QWidget, QSizePolicy, QFileDialog

from ui.common import BaseWidgetView, ImageButton
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import MaskManagerController
from util import image_converter as ic
from util.setting_manager import SettingManager


class PlateCaptureUnitView(BaseWidgetView):
    setting_manager = SettingManager()

    clicked = Signal()
    mask_manager_apply_clicked = Signal()
    clear_mask_info = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.origin_image: np.ndarray
        self.targets = []

    def closeEvent(self, event):
        if hasattr(self, "mask_manager") and self.mask_manager:
            self.mask_manager.close()

        super().closeEvent(event)

    def mouseReleaseEvent(self, event):
        size = self.size()
        pos = event.position()
        if (0 <= pos.x() <= size.width()) and (0 <= pos.y() <= size.height()):
            self.clicked.emit()

    def init_view(self):
        super().init_view()

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.is_selected = False
        self.has_image = False

        self._pixmap = QPixmap()  # 원본 이미지 유지하고 복사하여 사용
        self.masked_pixmap = QPixmap()
        self.lb_image = QLabel()

        self.cmb_target = QComboBox()
        self.cmb_target.setFixedWidth(150)
        img_lasso = ic.get_image_path("lasso.png")
        img_load_img = ic.get_image_path("img_load_box.png")
        img_trash_bin = ic.get_image_path("trash_bin.png")
        self.btn_edit_mask = ImageButton(image=img_lasso, size=(20, 20))
        self.btn_load_img = ImageButton(image=img_load_img, size=(20, 20))
        self.btn_trash_bin = ImageButton(image=img_trash_bin, size=(20, 20))
        self.btn_edit_mask.clicked.connect(self.open_mask_manager)
        self.btn_load_img.clicked.connect(self.open_file_dialog)
        lyt_bottom = QHBoxLayout()
        lyt_bottom.addStretch()
        lyt_bottom.addWidget(self.cmb_target)
        lyt_bottom.addWidget(self.btn_edit_mask)
        lyt_bottom.addWidget(self.btn_load_img)
        # lyt_bottom.addWidget(self.btn_trash_bin)
        lyt_bottom.addStretch()

        lyt = QVBoxLayout(self)
        lyt.addWidget(self.lb_image)
        lyt.addLayout(lyt_bottom)
        lyt.setContentsMargins(0, 0, 0, 0)

        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        lb_no_image = QLabel("NO IMAGE")
        lb_no_image.setFont(font)
        self.wig_no_image = QWidget()
        lyt_no_image = QHBoxLayout(self.wig_no_image)
        lyt_no_image.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        lyt_no_image.addWidget(lb_no_image)

        self.set_selected()

    @property
    def pixmap(self):
        return self._pixmap

    def set_selected(self, is_selected=True):
        if is_selected:
            self.lb_image.setStyleSheet("border: 4px solid #05FF00; border-radius: 10px;")
        else:
            self.lb_image.setStyleSheet("border: 2px solid black;")

    def update_label(self, pixmap):
        self.lb_image.setPixmap(pixmap.scaled(self.lb_image.size(), Qt.KeepAspectRatio))

    def set_pixmap(self, pixmap, no_image=False):
        if not isinstance(pixmap, QPixmap):
            self.set_no_image()
            return

        self.has_image = not no_image
        self._pixmap = pixmap
        self.update_label(self._pixmap)

    def set_image(self, image: np.ndarray):
        self.clear_mask_info.emit()
        self.origin_image = image
        pixmap = ic.array_to_q_pixmap(image, True)

        self.set_pixmap(pixmap)

    def set_no_image(self):
        pixmap = QPixmap(self.wig_no_image.size())
        self.wig_no_image.render(pixmap)
        self.set_pixmap(pixmap, no_image=True)

    def set_masked_pixmap(self, pixmap, x, y, width, height):
        self.masked_pixmap = pixmap.copy(x, y, width, height)
        self.update_label(self.masked_pixmap)

    def set_image_size(self, width=None, height=None):
        w = width if width else self.lb_image.width()
        h = height if height else self.lb_image.height()
        self.lb_image.setFixedSize(w, h)
        self.wig_no_image.setFixedSize(w, h)

        if not self.has_image:
            self.set_no_image()

    def open_mask_manager(self):
        if self.has_image:
            self.mask_manager = MaskManagerController(origin_image=self.origin_image)
            self.mask_manager.view.btn_apply.clicked.connect(lambda: self.mask_manager_apply_clicked.emit())
            self.mask_manager.view.exec()

    def open_file_dialog(self):
        base_path = self.setting_manager.get_path_to_load_image()
        base_path = base_path if base_path and os.path.exists(base_path) else ""

        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", base_path,
                                                    "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if image_path:
            path_list = image_path.split("/")[:-1]
            base_image_path = "/".join(path_list)
            self.setting_manager.set_path_to_load_image(base_image_path)

            image = ic.path_to_nd_array(image_path)
            self.set_image(image)

    def set_targets(self, targets):
        self.targets = targets
        self.cmb_target.clear()
        for target in targets:
            self.cmb_target.addItem(target["name"])

    def get_selected_target(self):
        selected_index = self.cmb_target.currentIndex()
        return self.targets[selected_index]

    def get_selected_target_id(self):
        return self.get_selected_target()["id"]
