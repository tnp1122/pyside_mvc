import os
from PySide6.QtCore import Signal
from PySide6.QtGui import Qt, QFont
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QSizePolicy, QFileDialog

from models import Image, Targets
from models.snapshot import Snapshot
from ui.common import BaseWidgetView, ImageButton
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import MaskManagerController

from util import local_storage_manager as lsm
from util.setting_manager import SettingManager


class ProcessUnitView(BaseWidgetView):
    setting_manager = SettingManager()

    clicked = Signal()
    clear_mask_info = Signal()

    def __init__(self, parent=None, snapshot: Snapshot = None):
        super().__init__(parent)

        self.targets = Targets()

        self.snapshot = snapshot
        self.snapshot.origin_image_changed.connect(self.update_pixmap)
        self.snapshot.processed.connect(self.update_pixmap)

    def closeEvent(self, event):
        if hasattr(self, "mask_manager") and self.mask_manager is not None:
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

        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.lb_image = QLabel("No Image")
        self.lb_image.setFont(font)
        self.lb_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cmb_target = QComboBox()
        self.cmb_target.setFixedWidth(150)
        self.cmb_target.currentTextChanged.connect(self.on_target_changed)
        img_lasso = lsm.get_static_image_path("lasso.png")
        img_load_img = lsm.get_static_image_path("img_load_box.png")
        img_trash_bin = lsm.get_static_image_path("trash_bin.png")
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

        self.set_selected()

    def set_selected(self, is_selected=True):
        if is_selected:
            self.lb_image.setStyleSheet("border: 4px solid #05FF00; border-radius: 10px;")
        else:
            self.lb_image.setStyleSheet("border: 2px solid black;")

    def update_pixmap(self):
        pixmap = self.snapshot.cropped_pixmap
        if pixmap:
            self.lb_image.setPixmap(pixmap.scaled(self.lb_image.size(), Qt.KeepAspectRatio))
        else:
            self.lb_image.setText("No Image")

    def set_image_size(self, width=None, height=None):
        w = width if width else self.lb_image.width()
        h = height if height else self.lb_image.height()
        self.lb_image.setFixedSize(w, h)

    def set_targets(self, targets):
        self.targets = targets
        self.cmb_target.clear()

        self.cmb_target.currentTextChanged.disconnect()
        for target in targets:
            self.cmb_target.addItem(target.name)
        self.cmb_target.currentTextChanged.connect(self.on_target_changed)

        if self.snapshot.target is not None:
            index, _ = self.targets.item_from_id(self.snapshot.target.id)
            self.cmb_target.setCurrentIndex(index)

    def on_target_changed(self, target_name):
        self.snapshot.set_target(self.targets.item_from_name(target_name)[1])

    def open_mask_manager(self):
        if self.snapshot.mask_editable:
            self.mask_manager = MaskManagerController(snapshot=self.snapshot)
            self.mask_manager.closed.connect(self.on_manager_closed)
            self.mask_manager.view.exec()

    def on_manager_closed(self):
        self.mask_manager = None
        self.update_pixmap()

    def open_file_dialog(self):
        base_path = self.setting_manager.get_path_to_load_image()
        base_path = base_path if base_path and os.path.exists(base_path) else ""

        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", base_path,
                                                    "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if image_path:
            path_list = image_path.split("/")[:-1]
            base_image_path = "/".join(path_list)
            self.setting_manager.set_path_to_load_image(base_image_path)

            image = Image().from_path(image_path)
            self.snapshot.init_origin_image(image)
