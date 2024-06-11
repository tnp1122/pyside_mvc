import copy
from datetime import datetime

import cv2
import numpy as np
import pandas as pd
from PySide6.QtCore import QObject, Signal, QRectF
from PySide6.QtGui import QPixmap

from models import Image, Target
from util import image_converter as ic, SnapshotDataManager
from util.local_storage_manager import TimelineDataManager
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

    def get_plate_info_dict(self):
        plate_info = {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "direction": self.direction,
            "additive_axes": self.additive_axes,
            "solvent_axes": self.solvent_axes
        }

        return plate_info

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
    flare_threshold_changed = Signal()

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

    @property
    def shape(self):
        return self.plate_image.shape if self.plate_image is not None else (10, 10, 3)

    def init_mask_info(self, plate_image: np.ndarray, plate: PlatePosition, mask_info: dict, set=True):
        self.plate_image = plate_image
        self.columns = plate.columns
        self.rows = plate.rows
        self.radius = mask_info.get("radius") or 35
        self.flare_threshold = mask_info.get("flare_threshold") or 200

        if set:
            self.set_mask()

    def change_plate_image(self, plate_image: np.ndarray):
        self.plate_image = plate_image
        self.on_mask_changed()

    def set_mask(self):
        shape = self.shape
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
        self.flare_threshold_changed.emit()

    def set_circle_mask(self, update_mask=False, emit=True):
        self.circle_mask = np.full(self.shape, 255, dtype=np.uint8)

        for y in self.rows:
            for x in self.columns:
                cv2.circle(self.circle_mask, (int(x), int(y)), self.radius, UNMASK_COLOR, thickness=cv2.FILLED)

        if update_mask:
            self.update_mask(emit)

    def set_flare_mask(self, update_mask=False, emit=True):
        b, g, r = cv2.split(self.plate_image)
        threshold = self.flare_threshold
        self.flare_mask = np.zeros(self.shape)
        self.flare_mask[(r > threshold) | (g > threshold) | (b > threshold)] = 255

        if update_mask:
            self.update_mask(emit)

    def set_custom_mask(self, mask: np.ndarray, emit=True):
        self.custom_mask = mask
        self.update_mask(emit)

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
        self.snapshot_loaded = False
        self.is_property_referenced = False

        self._mean_colors: np.ndarray = None  # 96개 평균 RGB 배열
        self._cropped_array: np.ndarray = None  # crop된 플레이트 원본 이미지 어레이
        self._mean_color_pixmap: QPixmap = None  # crop된 평균 RGB 픽스맵
        self._cropped_pixmap: QPixmap = None  # 1.crop된 플레이트 원본 픽스맵 / 2.crop된 평균 RGB 픽스맵
        self._origin_sized_masked_pixmap: QPixmap = None  # 원본 사이즈 마스크처리 된 픽스맵(마스크 매니저에 사용)

        self.snapshot_time: datetime = None

        self.plate_position.position_changed.connect(self.on_position_changed)
        self.plate_position.direction_changed.connect(self.on_position_changed)
        self.mask.mask_updated.connect(self.init_property_reference)

    def on_processed(self):
        plate_info = self.plate_position.get_plate_info_dict()
        mask_info = self.mask.get_mask_info_dict()
        plate_mask_info = dict(plate_info, **mask_info)

        SettingManager().set_mask_area_info(plate_mask_info)
        self.mask.update_mask()
        self.processed.emit()

    # 영역이나 마스킹이 변경되면 기존 mean_colors의 참조를 해제함
    def on_position_changed(self):
        self.mask.init_mask_info(self.cropped_array, self.plate_position, self.mask.get_mask_info_dict())
        self.init_property_reference()

    def init_property_reference(self):
        if self.is_property_referenced and self.mask_editable:
            self.is_property_referenced = False
            self._mean_colors = None
            self._cropped_array = None
            self._mean_color_pixmap = None
            self._origin_sized_masked_pixmap = None

    def init_origin_image(self, image: Image, has_alpha: bool = False):
        self.origin_image = image
        self.mask_editable = True
        self.snapshot_time = datetime.now()

        plate_mask_info = SettingManager().get_mask_area_info()

        plate = self.plate_position.init_plate_info(plate_mask_info)
        plate_image = self.cropped_array
        self.mask.init_mask_info(plate_image, plate, plate_mask_info)

        self.origin_image_changed.emit(image)

    def change_origin_image(self, image: Image):
        self.origin_image = image
        self.mask_editable = True
        self.snapshot_time = datetime.now()
        self.mask.change_plate_image(self.cropped_array)

        self.init_property_reference()
        # self.origin_image_changed.emit(image)

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
        mean_colors = copy.deepcopy(self.mean_colors)
        for rows in mean_colors:
            for column in rows:
                for i in range(3):
                    column[i] = int(column[i])

        mean_colors = {"mean_colors": mean_colors}
        snapshot_info = {
            "snapshot_info": {
                "x": 0,
                "y": 0,
                "width": w,
                "height": h,
                "direction": d,
                "radius": r,
                "flare_threshold": t,
                "snapshot_time": self.snapshot_time.strftime('%Y-%m-%dT%H:%M:%S')
            }
        }
        custom_mask = mask.custom_mask

        sdm = SnapshotDataManager(snapshot_path, snapshot_age, self.target.name)
        sdm.save_datas(plate_image, mean_colors, snapshot_info, custom_mask)

    def load_snapshot(self, snapshot_path: str, snapshot_age: int, target_name: str):
        sdm = SnapshotDataManager(snapshot_path, snapshot_age, target_name)
        plate_image: Image
        mask: np.ndarray

        plate_image, mean_colors, snapshot_info, mask = sdm.load_datas()

        snapshot_time_str = snapshot_info.get("snapshot_time") or "1970-01-01T00:00:00"
        self.snapshot_time = datetime.strptime(snapshot_time_str, '%Y-%m-%dT%H:%M:%S')
        plate_info_keys = ["x", "y", "width", "height", "direction"]
        mask_info_keys = ["radius", "flare_threshold"]
        plate_info = {key: value for key, value in snapshot_info.items() if key in plate_info_keys}
        mask_info = {key: value for key, value in snapshot_info.items() if key in mask_info_keys}

        self.mask_editable = plate_image.has_image
        self.snapshot_loaded = True
        self.origin_image = plate_image
        self._mean_colors = mean_colors

        self.set_plate_mask_info(plate_info, mask_info, mask)

    def set_plate_mask_info(self, plate_info, mask_info, mask):
        plate = self.plate_position.init_plate_info(plate_info)
        if self.mask_editable:
            self.mask.init_mask_info(self.cropped_array, plate, mask_info, set=True)
            self.mask.set_custom_mask(mask, emit=False)
        else:
            self.mask.init_mask_info(None, plate, mask_info, set=False)

        self.processed.emit()

    def init_plate_mask_info(self):
        self.init_property_reference()
        plate_info = {"x": 0, "y": 0, "width": 500, "height": 400, "direction": 1, "rotation": 0}
        mask_info = {"radius": 20, "flare_threshold": 200}
        init_shape = (500, 400, 3)
        new_mask = np.full(init_shape, 0, np.uint8)
        self.set_plate_mask_info(plate_info, mask_info, new_mask)

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
                # mean_color = np.mean(cell, axis=(0, 1)).astype(np.uint8)
                mean_color = np.mean(cell, axis=(0, 1)).astype(np.float32)
                # mean_color = np.mean(cell, axis=(0, 1))
                for i, color in enumerate(mean_color):
                    if isinstance(color, np.ma.core.MaskedConstant):
                        # mean_color[i] = np.uint8(0)
                        mean_color[i] = np.float32(0.0)
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
        mean_colors = copy.deepcopy(self.mean_colors)
        for j, circle_y in enumerate(plate.rows):
            for i, circle_x in enumerate(plate.columns):
                color = mean_colors[j][i]
                for k in range(3):
                    color[k] = np.float64(color[k])
                try:
                    cv2.circle(new_array, (int(circle_x), int(circle_y)), mask.radius, color, cv2.FILLED)
                except:
                    pass
                cv2.circle(new_array, (int(circle_x), int(circle_y)), mask.radius, color, cv2.FILLED)
        self._mean_color_pixmap = ic.array_to_q_pixmap(new_array)
        self.is_property_referenced = True

        return self._mean_color_pixmap

    @property
    # crop된 플레이트 원본 또는 평균색 픽스맵
    def cropped_pixmap(self) -> QPixmap:
        if self.mask_editable:
            return ic.array_to_q_pixmap(self.cropped_array)

        if self.snapshot_loaded:
            return self.mean_color_pixmap

        return None

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


class NotAIntValue(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class RoundModel(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        need_init = kwargs.get("need_init")
        if need_init:
            self.add_round()

    def set_rounds(self, rounds):
        for round_data in rounds:
            self.append(round_data)

    def add_round(self):
        last_round = self[-1] if self else {"interval": 1, "count": 100}
        self.append({"interval": last_round["interval"], "count": last_round["count"]})

        return self[-1]

    def remove_round(self, index):
        self.remove(self[index])

    def get_end_point(self, index=None):
        point = 0
        index = index if index is not None else len(self)
        for round_data in self[:index + 1]:
            point += round_data["interval"] * round_data["count"]

        return point

    def set_interval(self, index, interval):
        if not isinstance(interval, int):
            raise NotAIntValue("Failed to set interval")
        self[index]["interval"] = interval

    def set_count(self, index, count):
        if not isinstance(count, int):
            raise NotAIntValue("Failed to set interval")
        self[index]["count"] = count


class Timeline(dict):
    def __init__(self, timeline_name: str, target_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.timeline_data_manager = TimelineDataManager(timeline_name, target_name)

        self["rounds"] = RoundModel(need_init=True)
        self.num_cells = 96

        self.info_saved = False
        self.datas: pd.DataFrame
        self.init_data_frame()

    def init_plate_info(self, snapshot: Snapshot):
        x, y, w, h = snapshot.plate_position.get_plate_size()
        d = snapshot.plate_position.direction
        r, t = snapshot.mask.get_mask_info()
        self["x"] = x
        self["y"] = y
        self["width"] = w
        self["height"] = h
        self["direction"] = d
        self["radius"] = r
        self["flare_threshold"] = t

    def init_data_frame(self):
        columns = ["elapsed_time"]
        for idx in range(96):
            columns.extend([f"R{idx + 1}", f"G{idx + 1}", f"B{idx + 1}"])
        for idx in range(96):
            columns.append(f"ColorDistance{idx + 1}")
        for idx in range(96):
            columns.append(f"ColorVelocity{idx + 1}")

        self.datas = pd.DataFrame(columns=columns)

    def append_snapshot(self, snapshot: Snapshot):
        current_time = snapshot.snapshot_time.strftime("%y%m%d-%H%M%S.%f")[:-5]

        elapsed_time = self.elapsed_time
        new_row = [elapsed_time]

        for color_row in snapshot.mean_colors[::-1]:
            for cell_colors in color_row:
                for color in cell_colors:
                    new_row.append(color)
        for _ in range(self.num_cells * 2):
            new_row.append(np.float32(0))

        self.datas.loc[current_time] = new_row

        current_count = self.current_count
        if current_count > 1:
            init_colors = self.datas.iloc[0].iloc[1:289].values.reshape(self.num_cells, 3)
            current_colors = self.datas.iloc[current_count - 1].iloc[1:289].values.reshape(self.num_cells, 3)
            for idx in range(self.num_cells):
                init_color = init_colors[idx]
                current_color = current_colors[idx]
                distance = self.get_color_distance(init_color, current_color)
                self.datas.loc[current_time, f"ColorDistance{idx + 1}"] = distance
        if current_count > 2:
            # distance_idx = 96 * 3 + 1
            # for idx in range(self.num_cells):
            #     prev_distance = np.float32(self.datas.iloc[current_count - 2].iloc[distance_idx + idx])
            #     current_distance = np.float32(self.datas.iloc[current_count - 1].iloc[distance_idx + idx])
            #     self.datas.loc[current_time, f"ColorVelocity{idx + 1}"] = (current_distance - prev_distance) / prev_distance
            distance_idx = 96 * 3 + 1
            prev_distances = self.datas.iloc[current_count - 2, distance_idx:distance_idx + self.num_cells].astype(
                np.float32)
            current_distances = self.datas.iloc[current_count - 1, distance_idx:distance_idx + self.num_cells].astype(
                np.float32)
            color_velocities = (current_distances - prev_distances) / prev_distances / 100
            for idx, velocity in enumerate(color_velocities):
                self.datas.loc[current_time, f"ColorVelocity{idx + 1}"] = velocity

        self.save_timeline()

    def get_color_distance(self, color1, color2) -> np.float32:
        return np.float32(round(np.linalg.norm(color1 - color2), 3))

    def get_datas(self, indexes: list) -> (list, list[pd.DataFrame]):
        elapsed_times = self.datas["elapsed_time"].tolist()
        distance_datas = [f"ColorDistance{idx + 1}" for idx in indexes]
        velocity_datas = ([f"ColorVelocity{idx + 1}" for idx in indexes])
        return elapsed_times, [self.datas[distance_datas], self.datas[velocity_datas]]

    def save_timeline(self):
        if not self.info_saved:
            self.timeline_data_manager.save_timeline_info(self)
            self.info_saved = True

        mean_colors = self.datas.iloc[:, :288]
        self.timeline_data_manager.save_timeline(mean_colors)

    def load_timeline(self, snapshot_instance: Snapshot):
        timeline_info, mean_colors = self.timeline_data_manager.load_timeline()
        if mean_colors is None:
            return False

        for key, value in timeline_info.items():
            if key == "rounds":
                continue
            self[key] = value
        self["rounds"] = RoundModel(timeline_info["rounds"], need_init=False)

        snapshot_instance.plate_position.init_plate_info(timeline_info)
        snapshot_instance.mask.set_radius(self["radius"])
        snapshot_instance.mask.set_flare_threshold(self["flare_threshold"], False)

        self.datas = mean_colors.reindex(columns=self.datas.columns)

        init_colors = mean_colors.iloc[0].values.reshape(self.num_cells, 3)
        for row in self.datas.index[1:]:
            current_colors = self.datas.loc[row].iloc[1:289].values.reshape(self.num_cells, 3)
            for idx in range(self.num_cells):
                init_color = init_colors[idx]
                current_color = current_colors[idx]
                distance = self.get_color_distance(init_color, current_color)
                self.datas.loc[row, f"ColorDistance{idx + 1}"] = distance

        for idx in range(self.num_cells):
            self.datas[f"ColorVelocity{idx + 1}"] = self.datas[f"ColorDistance{idx + 1}"].pct_change(
                fill_method=None) / 100

        self.info_saved = True
        return True

    @property
    def rounds(self) -> RoundModel:
        return self["rounds"]

    @property
    def current_count(self):
        return len(self.datas)

    @property
    def current_round(self):
        total_count = 0

        for i, round_info in enumerate(self.rounds):
            total_count += round_info["count"]
            if self.current_count < total_count:
                return i
        return len(self.rounds) - 1

    @property
    def elapsed_time(self):
        elapsed_time = 0
        current_round = self.current_round
        if current_round > 0:
            for i in range(self.current_round):
                round_info = self.rounds[i]
                elapsed_time += round_info["interval"] * round_info["count"]

        elapsed_time += self.rounds[current_round]["interval"] * self.count_of_current_round
        return elapsed_time

    @property
    def end_count(self):
        count = 1
        for i in range(self.total_round):
            count += self.rounds[i]["count"]

        return count

    @property
    def total_round(self):
        return len(self.rounds)

    @property
    def count_of_current_round(self):
        if self.current_round == 0:
            return self.current_count

        total_count = 0
        for i in range(self.current_round):
            total_count += self.rounds[i]["count"]

        return self.current_count - total_count

    @property
    def total_count_of_current_round(self):
        return self.rounds[self.current_round]["count"]

    @property
    def current_interval(self):
        return self.rounds[self.current_round]["interval"]
