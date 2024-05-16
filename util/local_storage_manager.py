import gzip
import json
import os
import pickle

import cv2
import numpy as np
import pandas as pd

from model import Image
from . import image_converter as ic


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
    with gzip.open(file_name, "rb") as f:
        compressed_data = f.read()
        serialized_data = gzip.decompress(compressed_data)
        return pickle.loads(serialized_data)


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
                    mean_colors_data = pickle.loads(decompressed_data).get("mean_colors")

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


class TimelineDataManager:
    def __init__(self, timeline_name: str, target_name: str):
        storage_path = os.getenv("LOCAL_STORAGE_PATH")
        directory_path = get_absolute_path(storage_path, timeline_name)
        timeline_name = os.path.join(directory_path, target_name)

        self.ti_file_name = f"{timeline_name}.tigz"
        self.mc_file_name = f"{timeline_name}.mcgz"

    def save_timeline_info(self, timeline_info: dict):
        timeline_info_data = {"timeline_info": timeline_info}
        save_with_compress(timeline_info_data, self.ti_file_name)

    def save_timeline(self, mean_colors: pd.DataFrame):
        mean_colors_data = {"mean_colors": mean_colors}

        save_with_compress(mean_colors_data, self.mc_file_name)

    def load_timeline(self) -> (dict, pd.DataFrame):
        if not os.path.exists(self.mc_file_name):
            return None, None

        timeline_info = load_with_decompress(self.ti_file_name)["timeline_info"]
        mean_colors = load_with_decompress(self.mc_file_name)["mean_colors"]

        return timeline_info, mean_colors
