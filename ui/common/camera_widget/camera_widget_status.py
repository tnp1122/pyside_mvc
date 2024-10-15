import numpy as np
from PySide6.QtCore import QObject, Signal
from skimage import color

from models.snapshot import Snapshot
from util.enums import LabCorrectionType


class CameraWidgetStatus(QObject):
    wb_roi_changed = Signal(int, int, int, int)
    lab_correction_type_changed = Signal(LabCorrectionType)
    lab_reference_hole_index_changed = Signal(int)
    lab_reference_rgb_changed = Signal(int, int, int)
    lab_reference_lab_changed = Signal(int, int, int)

    use_mask_changed = Signal(bool)
    setting_visible_changed = Signal(bool)
    plate_border_visible_changed = Signal(bool)
    wb_roi_visible_changed = Signal(bool)
    lab_roi_visible_changed = Signal(bool)

    def __init__(
            self,
            parent=None,
            use_mask=True,
            setting_visible=True,
            plate_border_visible=True,
            wb_roi_visible=True,
            lab_roi_visible=True
    ):
        super().__init__(parent)

        self.snapshot_instance = Snapshot()

        self.wb_roi = [0, 0, 0, 0]
        self.lab_correction_type = LabCorrectionType.WHOLE_HALL_ROI
        self.lab_correction_reference_hole_index = None
        self.lab_correction_reference_rgb = [255, 255, 255]  # 0~255
        self.lab_correction_reference_lab = [100, 0, 0]  # 0~100, -128~128, -128~128

        self.use_mask = use_mask
        self.setting_visible = setting_visible
        self.plate_border_visible = plate_border_visible
        self.wb_roi_visible = wb_roi_visible
        self.lab_roi_visible = lab_roi_visible

    def get_lab_correction_reference_hole_index(self):
        if self.lab_correction_reference_hole_index is None:
            self.set_lab_correction_reference_hole_index(43)
        return self.lab_correction_reference_hole_index

    def set_wb_roi(self, x: int = None, y: int = None, width: int = None, height: int = None):
        temp = [x, y, width, height]
        for i, value in enumerate(temp):
            self.wb_roi[i] = value if value is not None else self.wb_roi[i]
        self.wb_roi_changed.emit(*self.wb_roi)
        return self.wb_roi

    def set_lab_correction_type(self, new_type: LabCorrectionType):
        self.lab_correction_type = new_type
        self.lab_correction_type_changed.emit(self.lab_correction_type)

    def set_lab_correction_reference_hole_index(self, value: int):
        self.lab_correction_reference_hole_index = value
        self.lab_reference_hole_index_changed.emit(self.lab_correction_reference_hole_index)
        if self.lab_correction_type != LabCorrectionType.SINGLE_HALL_ROI:
            self.set_lab_correction_type(LabCorrectionType.SINGLE_HALL_ROI)

    def set_lab_correction_reference_rgb(self, r=None, g=None, b=None):
        temp = [r, g, b]
        for i, value in enumerate(temp):
            self.lab_correction_reference_rgb[i] = value if value is not None else self.lab_correction_reference_rgb[i]

        rgb_normalized = np.array(self.lab_correction_reference_rgb) / 255.0
        rgb_normalized = rgb_normalized.reshape((1, 1, 3))
        lab = color.rgb2lab(rgb_normalized)
        self.lab_correction_reference_lab = lab[0, 0, :]

        self.lab_reference_rgb_changed.emit(*self.lab_correction_reference_rgb)
        self.lab_reference_lab_changed.emit(*self.lab_correction_reference_lab)

    def set_lab_correction_reference_lab(self, l=None, a=None, b=None):
        temp = [l, a, b]
        for i, value in enumerate(temp):
            self.lab_correction_reference_lab[i] = value if value is not None else self.lab_correction_reference_lab[i]

        lab = np.array(self.lab_correction_reference_lab).reshape((1, 1, 3))
        normalized_rgb = color.lab2rgb(lab)
        rgb = (normalized_rgb * 255)  # .astype(np.uint8)

        self.lab_correction_reference_rgb = rgb[0][0]
        self.lab_reference_rgb_changed.emit(*self.lab_correction_reference_rgb)
        self.lab_reference_lab_changed.emit(*self.lab_correction_reference_lab)

    def set_use_mask(self, status: bool):
        self.use_mask = status
        self.use_mask_changed.emit(self.use_mask)
        return self.use_mask

    def set_setting_visible(self, status: bool):
        self.setting_visible = status
        self.setting_visible_changed.emit(self.setting_visible)
        return self.setting_visible

    def set_plate_border_visible(self, status: bool):
        self.plate_border_visible = status
        self.plate_border_visible_changed.emit(self.plate_border_visible)
        return self.plate_border_visible

    def set_wb_roi_visible(self, status: bool):
        self.wb_roi_visible = status
        self.wb_roi_visible_changed.emit(self.wb_roi_visible)
        return self.wb_roi_visible

    def set_lab_roi_visible(self, status: bool):
        self.lab_roi_visible = status
        self.lab_roi_visible_changed.emit(self.lab_roi_visible)
        return self.lab_roi_visible

    def switch_use_mask(self):
        return self.set_use_mask(not self.use_mask)

    def switch_setting_visible(self):
        return self.set_setting_visible(not self.setting_visible)

    def switch_plate_border_visible(self):
        return self.set_plate_border_visible(not self.plate_border_visible)

    def switch_wb_roi_visible(self):
        return self.set_wb_roi_visible(not self.wb_roi_visible)

    def switch_lab_roi_visible(self):
        return self.set_lab_roi_visible(not self.lab_roi_visible)
