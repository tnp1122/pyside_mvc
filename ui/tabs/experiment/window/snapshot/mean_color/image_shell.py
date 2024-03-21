from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout


class ImageShell(QWidget):
    solvent_len = 12
    additive_len = 8

    width = 300
    height = 500
    title_font_size = 26

    def __init__(self, mean_colored_pixmap=None, cropped_original_pixmap=None, target_name=None, parent=None):
        super().__init__(parent)

        self.mean_colored_pixmap = mean_colored_pixmap
        self.cropped_original_pixmap = cropped_original_pixmap
        self.current_image = self.mean_colored_pixmap
        self.image_type = 0  # 0: 색 평균, 1: 실제 색

        lb_empty = QLabel("")
        lb_empty.setStyleSheet(f"font-size: {self.title_font_size}px;")

        self.wig_solvent_count = QWidget()
        self.wig_solvent_count.setFixedHeight(self.height)
        lyt_solvent_count = QVBoxLayout(self.wig_solvent_count)
        lyt_solvent_count.setSpacing(0)
        lyt_solvent_count.setContentsMargins(0, 0, 0, 0)
        for count in range(self.solvent_len, 0, -1):
            lb_solvent_index = QLabel(str(count))
            lb_solvent_index.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            lyt_solvent_count.addWidget(lb_solvent_index, stretch=1)

        lyt_left = QVBoxLayout()
        lyt_left.addWidget(lb_empty)
        lyt_left.addWidget(self.wig_solvent_count)
        lyt_left.addWidget(QLabel())

        self.lb_target = QLabel(target_name)
        self.lb_target.setStyleSheet(f"font-size: {self.title_font_size}px;")
        self.lb_target.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
        self.lb_image = QLabel()

        lyt_additive_count = QHBoxLayout()
        lyt_additive_count.setSpacing(0)
        lyt_additive_count.setContentsMargins(0, 0, 0, 0)
        for count in range(self.additive_len):
            lb_additive_index = QLabel(chr(ord("A") + count))
            lb_additive_index.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            lyt_additive_count.addWidget(lb_additive_index, stretch=1)

        lyt_right = QVBoxLayout()
        lyt_right.addWidget(self.lb_target)
        lyt_right.addWidget(self.lb_image)
        lyt_right.addLayout(lyt_additive_count)

        lyt = QHBoxLayout(self)
        lyt.addLayout(lyt_left)
        lyt.addLayout(lyt_right)
        lyt.addStretch()

        self.set_image_size(self.width, self.height)

    def set_image_shell(self, mean_colored_pixmap, cropped_original_pixmap, target_name):
        self.mean_colored_pixmap = mean_colored_pixmap
        self.cropped_original_pixmap = cropped_original_pixmap
        self.lb_target.setText(target_name)
        self.set_current_image_type(self.image_type)

    def set_current_image_type(self, index=0):
        self.image_type = index
        if index == 0:
            self.current_image = self.mean_colored_pixmap
        else:
            self.current_image = self.cropped_original_pixmap
        self.set_image(self.current_image)

    def set_image_size(self, width=None, height=None, set_image=True):
        w = width if width else self.width
        h = height if height else self.height

        self.width, self.height = w, h
        self.lb_image.setFixedSize(w, h)
        self.wig_solvent_count.setFixedHeight(h)

        if set_image:
            self.set_image(self.current_image)

    def set_image(self, pixmap):
        if not pixmap:
            return
        scaled_pixmap = pixmap.scaled(self.lb_image.size(), Qt.KeepAspectRatio)
        if scaled_pixmap.width() < self.width:
            self.set_image_size(width=scaled_pixmap.width(), set_image=False)
        else:
            self.set_image_size(height=scaled_pixmap.height(), set_image=False)
        self.lb_image.setPixmap(scaled_pixmap)

    def set_mean_colored_image(self):
        self.set_image(self.mean_colored_pixmap)

    def set_original_image(self):
        self.set_image(self.cropped_original_pixmap)
