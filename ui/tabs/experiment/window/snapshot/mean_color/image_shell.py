from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout

from model.snapshot import Snapshot


class ImageShell(QWidget):
    solvent_len = 12
    additive_len = 8

    width = 300
    height = 500
    title_font_size = 26

    def __init__(self, snapshot: Snapshot, parent=None):
        super().__init__(parent)

        self.snapshot = snapshot

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

        self.lb_target = QLabel(snapshot.target.name)
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
        lyt_right.addStretch()
        lyt_right.addWidget(self.lb_target)
        lyt_right.addWidget(self.lb_image)
        lyt_right.addLayout(lyt_additive_count)
        lyt_right.addStretch()

        lyt = QHBoxLayout(self)
        lyt.addLayout(lyt_left)
        lyt.addLayout(lyt_right)
        lyt.addStretch()

        self.snapshot.origin_image_changed.connect(self.set_image)
        self.snapshot.processed.connect(self.set_image)
        self.snapshot.target_changed.connect(lambda target: self.lb_target.setText(target.name))
        self.setVisible(False)

    def set_current_image_type(self, index):
        self.image_type = index
        if self.snapshot.mask_editable:
            self.set_image()

    def set_image(self):
        pixmap = self.current_pixmap
        if not pixmap:
            return

        self.lb_image.setFixedSize(self.width, self.height)
        scaled_pixmap = pixmap.scaled(self.lb_image.size(), Qt.KeepAspectRatio)
        w, h = scaled_pixmap.width(), scaled_pixmap.height()

        self.lb_image.setFixedSize(w, h)
        self.lb_image.setPixmap(scaled_pixmap)
        self.wig_solvent_count.setFixedHeight(h)
        self.setVisible(True)

    @property
    def current_pixmap(self):
        snapshot: Snapshot = self.snapshot
        if self.image_type == 0:
            return snapshot.mean_color_pixmap
        else:
            return snapshot.cropped_pixmap
