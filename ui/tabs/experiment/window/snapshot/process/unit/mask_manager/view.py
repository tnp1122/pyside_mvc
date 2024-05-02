from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFrame, QLabel

from model.snapshot import Snapshot, PlatePosition, Mask
from ui.common import MileStoneRadio, BaseDialogView, ColoredButton
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.draw_mask import DrawMask
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics.controller import MaskGraphicsController
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics.view.main import MaskGraphicsScene
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics.view.mask_area import MaskArea
from util.enums import MaskViewIndex


class MaskManagerView(BaseDialogView):
    width_pos_text = 50
    width_radius_text = 35

    def __init__(self, parent=None, snapshot: Snapshot = None):
        self.snapshot = snapshot
        super().__init__(parent)

        self.setWindowTitle("마스크 영역 지정")

        self.view_radio = MileStoneRadio(["원본", "마스킹 구역 지정", "마스킹 영역 보기"])
        self.btn_init_mask = ColoredButton("초기화", background_color="#FF4B4B")
        self.btn_init_mask.clicked.connect(self.on_init_mask_clicked)
        self.btn_init_mask.setVisible(False)
        self.btn_confirm = ColoredButton("확인")

        lyt_btn = QHBoxLayout()
        lyt_btn.addWidget(self.view_radio)
        lyt_btn.addWidget(self.btn_init_mask)
        lyt_btn.addWidget(self.btn_confirm)

        self.graphics = MaskGraphicsController(snapshot=self.snapshot)

        self.lyt_bottom_district = self.init_bottom_district()
        self.lyt_bottom_masking = self.init_bottom_masking()
        self.set_bottom_lyt(0)

        self.lyt = QVBoxLayout(self)
        self.lyt.addLayout(lyt_btn)
        self.lyt.addWidget(self.graphics.view)
        self.lyt.addLayout(self.lyt_bottom_district)
        self.lyt.addLayout(self.lyt_bottom_masking)

        self.init_text()

        self.connect_signal()

    def on_init_mask_clicked(self):
        self.snapshot.mask.set_mask()
        self.update_scene()

    def init_bottom_district(self):
        lyt = QHBoxLayout()
        self.btn_set_horizontal = QPushButton("가로")
        self.btn_set_vertical = QPushButton("세로")
        self.btn_circle = QPushButton("원 보기")
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)

        lb_x = QLabel("x")
        lb_y = QLabel("y")
        lb_w = QLabel("width")
        lb_h = QLabel("height")
        lb_r = QLabel("반지름")
        validator = QIntValidator(1, 9999)

        self.ET_x = QLineEdit()
        self.ET_y = QLineEdit()
        self.ET_w = QLineEdit()
        self.ET_h = QLineEdit()
        self.ET_r = QLineEdit()

        self.ET_x.setValidator(validator)
        self.ET_y.setValidator(validator)
        self.ET_w.setValidator(validator)
        self.ET_h.setValidator(validator)
        self.ET_r.setValidator(validator)

        self.ET_x.setFixedWidth(self.width_pos_text)
        self.ET_y.setFixedWidth(self.width_pos_text)
        self.ET_w.setFixedWidth(self.width_pos_text)
        self.ET_h.setFixedWidth(self.width_pos_text)
        self.ET_r.setFixedWidth(self.width_radius_text)

        lyt.addWidget(self.btn_set_horizontal)
        lyt.addWidget(self.btn_set_vertical)
        lyt.addWidget(self.btn_circle)
        lyt.addWidget(divider)
        lyt.addWidget(lb_x)
        lyt.addWidget(self.ET_x)
        lyt.addWidget(lb_y)
        lyt.addWidget(self.ET_y)
        lyt.addWidget(lb_w)
        lyt.addWidget(self.ET_w)
        lyt.addWidget(lb_h)
        lyt.addWidget(self.ET_h)
        lyt.addWidget(lb_r)
        lyt.addWidget(self.ET_r)
        lyt.addStretch()

        return lyt

    def init_bottom_masking(self):
        lyt = QHBoxLayout()
        self.btn_open_masking = QPushButton("마스킹 영역 수정")
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)

        lb_threshold = QLabel("threshold")
        self.ET_threshold = QLineEdit()
        validator = QIntValidator(1, 255)
        self.ET_threshold.setValidator(validator)
        self.ET_threshold.setFixedWidth(40)

        lyt.addWidget(self.btn_open_masking)
        lyt.addWidget(divider)
        lyt.addWidget(lb_threshold)
        lyt.addWidget(self.ET_threshold)
        lyt.addStretch()

        return lyt

    def closeEvent(self, event):
        self.graphics.close()
        if hasattr(self, "masking_view") and self.masking_view is not None:
            self.masking_view = None

        super().closeEvent(event)

    def init_text(self):
        self.update_area_position_text()

        mask: Mask = self.snapshot.mask
        radius, threshold = mask.get_mask_info()
        self.ET_r.setText(str(radius))
        self.ET_threshold.setText(str(threshold))

    def update_area_position_text(self):
        plate: PlatePosition = self.snapshot.plate_position
        x, y, w, h = plate.get_plate_size()
        self.ET_x.setText(str(x))
        self.ET_y.setText(str(y))
        self.ET_w.setText(str(w))
        self.ET_h.setText(str(h))

    def set_bottom_lyt(self, index):
        if index == 0:
            self.set_bottom_lyt_visible(1, False)
            self.set_bottom_lyt_visible(2, False)
        elif index == 1:
            self.set_bottom_lyt_visible(1, True)
            self.set_bottom_lyt_visible(2, False)
        else:
            self.set_bottom_lyt_visible(1, False)
            self.set_bottom_lyt_visible(2, True)

    def set_bottom_lyt_visible(self, index, visible):
        if index == 1:
            lyt = self.lyt_bottom_district
        else:
            lyt = self.lyt_bottom_masking

        for idx in range(lyt.count() - 1):
            widget = lyt.itemAt(idx).widget()
            widget.setVisible(visible)

    def connect_signal(self):
        self.circle_visible = False
        plate: PlatePosition = self.snapshot.plate_position
        mask: Mask = self.snapshot.mask

        self.view_radio.selected.connect(self.on_select_changed)
        self.btn_set_horizontal.clicked.connect(lambda: self.set_direction(0))
        self.btn_set_vertical.clicked.connect(lambda: self.set_direction(1))
        self.btn_circle.clicked.connect(self.toggle_circle_visibility)
        self.btn_open_masking.clicked.connect(self.open_masking_view)
        self.ET_x.textChanged.connect(lambda x: plate.set_position(x=int(x or 0)))
        self.ET_y.textChanged.connect(lambda y: plate.set_position(y=int(y or 0)))
        self.ET_w.textChanged.connect(lambda w: plate.set_position(width=(int(w or 0))))
        self.ET_h.textChanged.connect(lambda h: plate.set_position(height=(int(h or 0))))
        self.ET_r.textChanged.connect(lambda r: mask.set_radius(int(r or 0)))
        self.ET_threshold.textChanged.connect(lambda t: mask.set_flare_threshold(int(t)))

        plate.position_changed.connect(self.update_area_position_text)
        mask.flare_threshold_changed.connect(self.update_scene)

    def on_select_changed(self, index):
        view_index = MaskViewIndex(index)
        self.set_bottom_lyt(index)

        graphics: MaskGraphicsController = self.graphics
        graphics.view_handler.set_current_view(view_index)
        self.btn_init_mask.setVisible(False)

        if view_index == MaskViewIndex.DISTRICT:
            graphics.model.is_border_adjustable = True
        else:
            graphics.model.is_border_adjustable = False

        if view_index == MaskViewIndex.MASK:
            self.update_scene()
            self.btn_init_mask.setVisible(True)

    def set_direction(self, index):
        plate: PlatePosition = self.snapshot.plate_position
        plate.set_direction(index)

    def toggle_circle_visibility(self):
        self.circle_visible = not self.circle_visible
        area: MaskArea = self.graphics.view.scene.area
        area.set_circle_visible(self.circle_visible)

    def open_masking_view(self):
        def handle_custom_mask(masking_view: DrawMask):
            if masking_view is not None:
                masking_view.closed.disconnect()

            self.snapshot.mask.update_mask()
            self.update_scene()

        masking_view = DrawMask(self.snapshot)
        masking_view.closed.connect(lambda: handle_custom_mask(masking_view))
        masking_view.open_window()

    def update_scene(self):
        scene: MaskGraphicsScene = self.graphics.view.scene
        scene.update_masking_view()
