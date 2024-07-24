import gzip
import io
import json
import os
import pickle

import cv2
import numpy as np
import pandas as pd
from PySide6.QtCore import QThread, Signal, QObject

from models import Image
from . import image_converter as ic


class ModuleFixUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith("model.snapshot"):
            module = module.replace("model.snapshot", "models.snapshot", 1)

        return super().find_class(module, name)


def loads_with_pickle(object):
    return ModuleFixUnpickler(io.BytesIO(object)).load()


def get_static_image_path(image_name: str) -> str:
    image_path = os.path.join(os.getcwd(), f"static/image/{image_name}")
    if os.path.exists(image_path):
        return image_path
    return os.path.join(os.getcwd(), f"pit/static/image/{image_name}")


def get_absolute_path(main_path="", sub_path="", make_directory=True) -> str:
    absolute_path = os.getcwd()
    if main_path:
        absolute_path = os.path.join(absolute_path, main_path)
    if sub_path:
        absolute_path = os.path.join(absolute_path, sub_path)
    if make_directory and not os.path.exists(absolute_path):
        os.makedirs(absolute_path)
    return absolute_path


def save_with_compress(data, file_name):
    serialized_data = pickle.dumps(data)
    compressed_data = gzip.compress(serialized_data)
    with gzip.open(file_name, "wb") as f:
        f.write(compressed_data)


def load_with_decompress(file_name):
    try:
        with gzip.open(file_name, "rb") as f:
            compressed_data = f.read()
            serialized_data = gzip.decompress(compressed_data)
            # return pickle.loads(serialized_data)
            return loads_with_pickle(serialized_data)
    except Exception as e:
        return None


class SnapshotDataManager:
    def __init__(self, snapshot_name: str, snapshot_age: int, target_name: str):
        storage_path = os.getenv("LOCAL_STORAGE_PATH")
        directory_path = get_absolute_path(storage_path, snapshot_name)
        capture_name = f"{snapshot_age}H_{target_name}"

        snapshot_path = os.path.join(directory_path, capture_name)
        self.path_image_jpg = f"{snapshot_path}.jpg"
        self.path_image_png = f"{snapshot_path}.png"  # will be depreciated
        self.path_mean_colors = f"{snapshot_path}.mc"  # will be depreciated
        self.path_mean_colors_gz = f"{snapshot_path}.mcgz"
        self.path_snapshot_info = f"{snapshot_path}.dat"
        self.path_mask = f"{snapshot_path}.npz"
        self.path_mcmi = f"{snapshot_path}.mcmi"

    def save_datas(self, plate_image: np.ndarray, mean_colors: dict, snapshot_info: dict, mask: np.ndarray):
        converted_image = cv2.cvtColor(plate_image, cv2.COLOR_RGB2BGR)
        ic.img_write(self.path_image_jpg, converted_image)

        serialized_data = pickle.dumps(mean_colors)
        compressed_data = gzip.compress(serialized_data)
        with gzip.open(self.path_mean_colors_gz, "wb") as f:
            f.write(compressed_data)

        with open(self.path_snapshot_info, "w") as snapshot_file:
            json.dump(snapshot_info, snapshot_file)

        np.savez_compressed(self.path_mask, data=mask)

    def load_datas(self) -> (Image, dict, dict, np.ndarray):
        try:
            plate_image = Image().from_path(self.path_image_jpg)
        except:
            try:
                plate_image = Image().from_path(self.path_image_png)
            except:
                plate_image = Image()

        try:
            try:
                with gzip.open(self.path_mean_colors_gz, "rb") as f:
                    compressed_data = f.read()
                    decompressed_data = gzip.decompress(compressed_data)
                    # mean_colors_data = pickle.loads(decompressed_data).get("mean_colors")
                    mean_colors_data = loads_with_pickle(decompressed_data).get("mean_colors")

            except:
                with open(self.path_mean_colors, "r") as mean_colors_file:
                    mean_colors_data = json.load(mean_colors_file).get("mean_colors")

            with open(self.path_snapshot_info, "r") as snapshot_info_file:
                snapshot_info_data = json.load(snapshot_info_file).get("snapshot_info")
        except:
            with open(self.path_mcmi, "r") as mcmi_file:
                mcmi = json.load(mcmi_file)
                mean_colors_data = mcmi.get("mean_colors")
                snapshot_info_data = mcmi.get("mask_info")

                def get_new_key(key):
                    if key == "r":
                        return "radius"
                    else:
                        return key

                snapshot_info_data = {
                    get_new_key(key): value for key, value in snapshot_info_data.items()
                }
                snapshot_info_data["width"] = plate_image.array.shape[0]
                snapshot_info_data["height"] = plate_image.shape[1]

        mask = np.load(self.path_mask)["data"]
        return plate_image, mean_colors_data, snapshot_info_data, mask


class TimeLineLoadWorker(QThread):
    finished = Signal(dict, pd.DataFrame)

    def __init__(self, timeline, snapshot_instance, timeline_info, mean_colors, parent=None):
        super().__init__(parent)
        self.timeline = timeline
        self.snapshot_instance = snapshot_instance
        self.timeline_info = timeline_info
        self.mean_colors = mean_colors

    def run(self):
        datas = self.calculate_timeline_datas()
        self.finished.emit(self.timeline_info, datas)
        self.exec()

    def calculate_timeline_datas(self):
        datas = self.mean_colors.reindex(columns=self.timeline.datas.columns)
        num_cells = self.timeline.num_cells

        init_colors = datas.iloc[0, 1:289].values.reshape(num_cells, 3)

        current_colors_matrix = datas.iloc[1:, 1:289].values.reshape(-1, num_cells, 3)
        distances = np.linalg.norm(init_colors - current_colors_matrix, axis=2)

        for idx in range(num_cells):
            datas.iloc[1:, datas.columns.get_loc(f"ColorDistance{idx + 1}")] = distances[:, idx]

        distance_columns = [f"ColorDistance{idx + 1}" for idx in range(num_cells)]
        prev_distances = datas.iloc[1:-1, datas.columns.get_loc(distance_columns[0]):datas.columns.get_loc(
            distance_columns[-1]) + 1].astype(np.float32).values
        current_distances = datas.iloc[2:, datas.columns.get_loc(distance_columns[0]):datas.columns.get_loc(
            distance_columns[-1]) + 1].astype(np.float32).values
        prev_distances[prev_distances == 0] = np.finfo(np.float32).eps
        color_velocities = (current_distances - prev_distances) / prev_distances

        for idx, col in enumerate(distance_columns):
            datas.iloc[2:, datas.columns.get_loc(f"ColorVelocity{idx + 1}")] = color_velocities[:, idx]

        return datas

    def get_color_distance(self, color1, color2) -> np.float32:
        return np.float32(round(np.linalg.norm(color1 - color2), 3))


class TimelineDataManager(QObject):
    timeline_loaded = Signal

    def __init__(self):
        super().__init__()

    def get_file_name(self, timeline_name, target_name):
        storage_path = os.getenv("LOCAL_STORAGE_PATH")
        directory_path = get_absolute_path(storage_path, timeline_name)
        file_name = os.path.join(directory_path, target_name)

        camera_setting_file_name = f"{file_name}.csgz"
        ti_file_name = f"{file_name}.tigz"
        mc_file_name = f"{file_name}.mcgz"

        return camera_setting_file_name, ti_file_name, mc_file_name

    def save_timeline_info(self, camera_settings: dict, cs_file_name: str, timeline_info: dict, ti_file_name: str):
        camera_settings_data = {"camera_settings": camera_settings}
        timeline_info_data = {"timeline_info": timeline_info}
        save_with_compress(camera_settings_data, cs_file_name)
        save_with_compress(timeline_info_data, ti_file_name)

    def save_timeline(self, mean_colors: pd.DataFrame, mc_file_name: str):
        mean_colors_data = {"mean_colors": mean_colors}
        save_with_compress(mean_colors_data, mc_file_name)

    def load_timeline(self, timeline, snapshot_instance, cs_file_name, ti_file_name: str, mc_file_name: str) -> (
    dict, pd.DataFrame):
        if not os.path.exists(mc_file_name):
            return None, None

        try:
            camera_settings = load_with_decompress(cs_file_name).get["camera_settings"]
        except:
            camera_settings = None
        timeline_info = load_with_decompress(ti_file_name)["timeline_info"]
        mean_colors = load_with_decompress(mc_file_name)["mean_colors"]
        worker = TimeLineLoadWorker(timeline, snapshot_instance, timeline_info, mean_colors)

        return worker, camera_settings
