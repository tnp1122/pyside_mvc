import os

from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, Qt, QFont
from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QWidget, QSizePolicy, QFileDialog

from ui.common import BaseWidgetView, ImageButton
from util.setting_manager import SettingManager


class PlateCaptureUnitView(BaseWidgetView):
    setting_manager = SettingManager()

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_name = ""

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

        self.pixmap = QPixmap()
        self.lb_image = QLabel()

        self.cmb_target = QComboBox()
        self.cmb_target.setFixedWidth(150)
        img_lasso = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 "../../../../../../../static/image/lasso.png")
        img_load_img = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    "../../../../../../../static/image/img_load_box.png")
        img_trash_bin = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                     "../../../../../../../static/image/trash_bin.png")
        self.btn_edit_mask = ImageButton(image=img_lasso, size=(20, 20))
        self.btn_load_img = ImageButton(image=img_load_img, size=(20, 20))
        self.btn_trash_bin = ImageButton(image=img_trash_bin, size=(20, 20))
        self.btn_load_img.clicked.connect(self.open_file_dialog)
        lyt_bottom = QHBoxLayout()
        lyt_bottom.addStretch()
        lyt_bottom.addWidget(self.cmb_target)
        lyt_bottom.addWidget(self.btn_edit_mask)
        lyt_bottom.addWidget(self.btn_load_img)
        lyt_bottom.addWidget(self.btn_trash_bin)
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

    def set_selected(self, is_selected=True):
        if is_selected:
            self.lb_image.setStyleSheet("border: 4px solid #05FF00; border-radius: 10px;")
        else:
            self.lb_image.setStyleSheet("border: 2px solid black;")

    def set_image(self, image, no_image=False):
        self.has_image = not no_image
        if isinstance(image, QPixmap):
            self.pixmap = image
        else:
            self.pixmap = QPixmap(image)
        self.lb_image.setPixmap(self.pixmap.scaled(self.lb_image.size(), Qt.KeepAspectRatio))

    def set_no_image(self):
        pixmap = QPixmap(self.wig_no_image.size())
        self.wig_no_image.render(pixmap)
        self.set_image(pixmap, no_image=True)

    def set_image_size(self, width=None, height=None):
        w = width if width else self.lb_image.width()
        h = height if height else self.lb_image.height()
        self.lb_image.setFixedSize(w, h)
        self.wig_no_image.setFixedSize(w, h)

        if not self.has_image:
            self.set_no_image()

    def open_mask_manager(self):
        if self.has_image:
            pass

    def open_file_dialog(self):
        image_path = self.setting_manager.get_path_to_load_image()
        image_path = image_path if image_path and os.path.exists(image_path) else ""

        self.file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", image_path,
                                                        "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if self.file_name:
            path_list = self.file_name.split("/")[:-1]
            image_path = "/".join(path_list)
            self.setting_manager.set_path_to_load_image(image_path)

            pixmap = QPixmap(self.file_name)
            self.set_image(pixmap)
