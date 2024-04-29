from datetime import datetime

import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal, QRectF
from PySide6.QtGui import QPixmap

from model import Image, Target
from util import image_converter as ic, SnapshotDataManager
from util.setting_manager import SettingManager

MASK_COLOR = (255, 255, 255)
UNMASK_COLOR = (0, 0, 0)


# origin_image 안에서 플레이트의 위치
class PlatePosition(QObject):
    position_changed = Signal(bool)  # update_graphics: bool
    direction_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.direction = 0

    def init_plate_info(self, plate_info: dict):
        x, y = plate_info.get("x") or 0, plate_info.get("y") or 0
        self.x = x
        self.y = y
        self.width = plate_info.get("width") or 1000
        self.height = plate_info.get("height") or 600
        self.direction = plate_info.get("direction") or 1

        return self

    def get_plate_mask_info_dict(self):
        plate_mask_info = {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "direction": self.direction,
            "additive_axes": self.additive_axes,
            "solvent_axes": self.solvent_axes
        }

        return plate_mask_info

    def set_position(self, x=None, y=None, width=None, height=None, update_graphics=True):
        self.x = x or self.x
        self.y = y or self.y
        self.width = width or self.width
        self.height = height or self.height
        self.position_changed.emit(update_graphics)

    def set_position_with_qrect(self, rect: QRectF, update_graphics=True):
        x, y, w, h = round(rect.x()), round(rect.y()), round(rect.width()), round(rect.height())
        if self.direction == 0:
            self.set_position(x, y, w, h, update_graphics)
        else:
            self.set_position(x, y, h, w, update_graphics)

    def set_direction(self, direction: int = 0):
        if self.direction != direction:
            self.direction = direction
            self.direction_changed.emit(self.direction)

    def get_crop_area(self):  # 이미지 crop 용
        if self.direction == 0:
            width, height = round(self.width), round(self.height)
        else:
            width, height = round(self.height), round(self.width)
        return round(self.x), round(self.y), width, height

    def get_axis_position(self):  # graphics의 축 렌더링용 좌표
        if self.direction == 0:
            x, y = round(self.x), round(self.y)
        else:
            x, y = round(self.y), round(self.x)
        return x, y, round(self.width), round(self.height)

    def get_plate_size(self):  # 실제 플레이트 사이즈
        return round(self.x), round(self.y), round(self.width), round(self.height)

    def _get_axes(self, length, count):
        interval = length / count
        return [interval / 2 + i * interval for i in range(count)]

    @property
    def rows(self):
        if self.direction == 0:
            return self._get_axes(self.height, 8)
        else:
            return self._get_axes(self.width, 12)

    @property
    def columns(self):
        if self.direction == 0:
            return self._get_axes(self.width, 12)
        else:
            return self._get_axes(self.height, 8)

    @property
    def additive_axes(self):  # width, 8개
        if self.direction == 0:
            return self.rows
        else:
            return self.columns

    @property
    def solvent_axes(self):  # height, 12개
        if self.direction == 0:
            return self.columns
        else:
            return self.rows


class Mask(QObject):
    radius_changed = Signal(int)
    flare_threshold_changed = Signal(int)

    mask_updated = Signal()

    def __init__(self):
        super().__init__()
        self.plate_image = None
        self.columns = []
        self.rows = []
        self.radius = 0
        self.flare_threshold = 0

    @property
    def mask_filled_array(self):
        return self.masked_array.filled(0).astype(np.uint8)

    @property
    def mask_filled_pixmap(self):
        return ic.array_to_q_pixmap(self.mask_filled_array)

    @property
    def basic_mask(self):
        return np.logical_or(self.circle_mask, self.flare_mask)

    def init_mask_info(self, plate_image: np.ndarray, plate: PlatePosition, mask_info: dict):
        self.plate_image = plate_image
        self.columns = plate.columns
        self.rows = plate.rows
        self.radius = mask_info.get("radius") or 35
        self.flare_threshold = mask_info.get("flare_threshold") or 200

        self.set_mask()

    def set_mask(self):
        shape = self.plate_image.shape if self.plate_image is not None else (10, 10, 3)
        self.circle_mask = np.full(shape, 255, np.uint8)
        self.flare_mask = np.full(shape, 0, np.uint8)
        self.custom_mask = np.full(shape, 0, np.uint8)
        self.masked_array: np.ndarray

        self.set_circle_mask()
        self.set_flare_mask(update_mask=True, emit=True)

    def get_mask_info(self):
        return self.radius, self.flare_threshold

    def get_mask_info_dict(self):
        return {"radius": self.radius, "flare_threshold": self.flare_threshold}

    def set_radius(self, radius: int):
        self.radius = radius
        self.set_circle_mask(True)
        self.radius_changed.emit(radius)

    def set_flare_threshold(self, flare_threshold: int, emit=True):
        self.flare_threshold = flare_threshold
        self.set_flare_mask(update_mask=True, emit=emit)

    def set_circle_mask(self, update_mask=False, emit=True):
        self.circle_mask = np.full_like(self.plate_image[:, :, :3], 255, dtype=np.uint8)

        for y in self.rows:
            for x in self.columns:
                cv2.circle(self.circle_mask, (int(x), int(y)), self.radius, UNMASK_COLOR, thickness=cv2.FILLED)

        if update_mask:
            self.update_mask(emit)

    def set_flare_mask(self, update_mask=False, emit=True):
        _, flare_mask = cv2.threshold(self.plate_image, self.flare_threshold, 255, cv2.THRESH_BINARY_INV)
        self.flare_mask = cv2.bitwise_not(flare_mask)

        if update_mask:
            self.update_mask(emit)

    def set_custom_mask(self, mask: np.ndarray):
        self.custom_mask = mask
        self.update_mask()

    def update_mask(self, emit=True):
        self.on_mask_changed()

        if emit:
            self.mask_updated.emit()

    def on_mask_changed(self):
        combined_mask = np.logical_or(self.basic_mask, self.custom_mask)
        self.masked_array = np.ma.masked_array(self.plate_image, combined_mask)


class Snapshot(QObject):
    origin_image_changed = Signal(Image)  # 원본 이미지 변경시 발생
    target_changed = Signal(Target)  # 타겟 물질 변경시 발생
    processed = Signal()  # 마스크 매니저 윈도우 닫히면 발생: 처리 탭, 평균색 탭, 색차이 탭 업데이트 슬롯으로 연결

    def __init__(self, image: np.ndarray = None, has_alpha: bool = False):
        super().__init__()
        self.origin_image = Image(image, has_alpha)
        self.plate_position = PlatePosition()
        self.mask = Mask()
        self.target: Target = None
        self.mask_editable = False
        self.is_property_referenced = False

        self._mean_colors: np.ndarray = None  # 96개 평균 RGB 배열
        self._cropped_array: np.ndarray = None  # crop된 플레이트 원본 이미지 어레이
        self._mean_color_pixmap: QPixmap = None  # crop된 평균 RGB 픽스맵
        self._cropped_pixmap: QPixmap = None  # 1.crop된 플레이트 원본 픽스맵 / 2.crop된 평균 RGB 픽스맵
        self._origin_sized_masked_pixmap: QPixmap = None  # 원본 사이즈 마스크처리 된 픽스맵(마스크 매니저에 사용)

        self.interval: int = None
        self.snapshot_time: datetime = None

        self.plate_position.position_changed.connect(self.on_position_changed)
        self.plate_position.direction_changed.connect(self.on_position_changed)
        self.mask.mask_updated.connect(self.init_property_reference)

    def on_processed(self):
        self.mask.update_mask()
        self.processed.emit()

    # 영역이나 마스킹이 변경되면 기존 mean_colors의 참조를 해제함
    def on_position_changed(self):
        self.mask.init_mask_info(self.cropped_array, self.plate_position, self.mask.get_mask_info_dict())
        self.init_property_reference()

    def init_property_reference(self):
        if self.is_property_referenced:
            self.is_property_referenced = False
            self._mean_colors = None
            self._cropped_array = None
            self._mean_color_pixmap = None
            self._origin_sized_masked_pixmap = None

    def init_origin_image(self, image: Image, has_alpha: bool = False):
        self.origin_image = image
        self.mask_editable = True

        plate_mask_info = SettingManager().get_mask_area_info()

        plate = self.plate_position.init_plate_info(plate_mask_info)
        plate_image = self.cropped_array
        self.mask.init_mask_info(plate_image, plate, plate_mask_info)

        self.origin_image_changed.emit(image)

    def save_snapshot(self, snapshot_path: str, snapshot_age: int):
        plate: PlatePosition = self.plate_position
        mask: Mask = self.mask
        if plate.direction == 0:
            w, h = self.cropped_array.shape[1], self.cropped_array.shape[0]
        else:
            w, h = self.cropped_array.shape[0], self.cropped_array.shape[1]

        d = plate.direction
        r, t = mask.get_mask_info()

        plate_image = self.cropped_array
        mean_colors = {"mean_colors": self.mean_colors}
        snapshot_info = {
            "snapshot_info": {
                "x": 0, "y": 0, "width": w, "height": h, "direction": d, "radius": r, "flare_threshold": t
            }
        }
        mask_array = mask.masked_array.mask

        sdm = SnapshotDataManager(snapshot_path, snapshot_age, self.target.name)
        sdm.save_datas(plate_image, mean_colors, snapshot_info, mask_array)

    def load_snapshot(self, snapshot_path: str, snapshot_age: int, target_name: str):
        sdm = SnapshotDataManager(snapshot_path, snapshot_age, target_name)
        plate_image, _, snapshot_info, mask = sdm.load_datas()

        plate_info_keys = ["x", "y", "width", "height", "direction"]
        mask_info_keys = ["radius", "flare_threshold"]
        plate_info = {key: value for key, value in snapshot_info.items() if key in plate_info_keys}
        mask_info = {key: value for key, value in snapshot_info.items() if key in mask_info_keys}

        self.origin_image = plate_image
        self.mask_editable = True
        plate = self.plate_position.init_plate_info(plate_info)
        self.mask.init_mask_info(self.cropped_array, plate, mask_info)

        self.origin_image_changed.emit(plate_image)

    def set_target(self, target: Target):
        self.target = target
        self.target_changed.emit(target)

    @property
    def mean_colors(self):
        if self._mean_colors is not None:
            return self._mean_colors

        self._mean_colors = self.calculate_mean_colors()
        self.is_property_referenced = True
        return self._mean_colors

    def calculate_mean_colors(self):
        plate = self.plate_position
        mask = self.mask
        r, columns, rows = mask.radius, plate.columns, plate.rows
        plate_image = self.mask.masked_array

        mean_colors = []
        for j, circle_y in enumerate(rows):
            mean_colors.append([])
            for circle_x in columns:
                x1, x2 = int(circle_x - r), int(circle_x + r)
                y1, y2 = int(circle_y - r), int(circle_y + r)
                cell = plate_image[y1:y2, x1:x2]
                mean_color = np.mean(cell, axis=(0, 1))
                for i, color in enumerate(mean_color):
                    if isinstance(color, np.ma.core.MaskedConstant):
                        mean_color[i] = np.float64(0.0)
                mean_colors[j].append(list(mean_color))

        return mean_colors

    @property
    def cropped_array(self) -> np.ndarray:
        if self._cropped_array is not None:
            return self._cropped_array

        plate: PlatePosition = self.plate_position
        self._cropped_array = self.origin_image.cropped(*plate.get_crop_area())
        self.is_property_referenced = True

        return self._cropped_array

    @property
    # 평균색 픽스맵
    def mean_color_pixmap(self) -> QPixmap:
        if self._mean_color_pixmap is not None:
            return self._mean_color_pixmap

        plate: PlatePosition = self.plate_position
        mask: Mask = self.mask
        _, _, width, height = plate.get_crop_area()

        new_array = np.full((height, width, 3), 0, dtype=np.uint8)
        for j, circle_y in enumerate(plate.rows):
            for i, circle_x in enumerate(plate.columns):
                mean_color = self.mean_colors[j][i]
                try:
                    cv2.circle(new_array, (int(circle_x), int(circle_y)), mask.radius, mean_color, cv2.FILLED)
                except:
                    pass
        self._mean_color_pixmap = ic.array_to_q_pixmap(new_array)
        self.is_property_referenced = True

        return self._mean_color_pixmap

    @property
    # crop된 플레이트 원본 또는 평균색 픽스맵
    def cropped_pixmap(self) -> QPixmap:
        if self.origin_image:
            return ic.array_to_q_pixmap(self.cropped_array)

        return self.mean_color_pixmap

    @property
    def origin_sized_masked_pixmap(self) -> QPixmap:
        if self._origin_sized_masked_pixmap is not None:
            return self._origin_sized_masked_pixmap

        background = np.full_like(self.origin_image.array, 0)
        x, y, width, height = self.plate_position.get_crop_area()
        background[y:y + height, x:x + width] = self.mask.mask_filled_array

        self._origin_sized_masked_pixmap = ic.array_to_q_pixmap(background)
        self.is_property_referenced = True

        return self._origin_sized_masked_pixmap

    # def set_interval(self, interval: int):
    #     self.interval = interval
    #
    # def set_snapshot_time(self, snapshot_time: datetime):
    #     self.snapshot_time = snapshot_time
