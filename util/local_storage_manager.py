import json
import os

import cv2
import numpy as np

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


class SnapshotDataManager:
    def __init__(self, snapshot_path: str, snapshot_age: int, target_name: str):
        storage_path = os.getenv("LOCAL_STORAGE_PATH")
        directory_path = get_absolute_path(storage_path, snapshot_path)
        capture_name = f"{snapshot_age}H_{target_name}"

        snapshot_path = os.path.join(directory_path, capture_name)
        self.path_image = f"{snapshot_path}.png"
        self.path_mean_colors = f"{snapshot_path}.mc"
        self.path_snapshot_info = f"{snapshot_path}.dat"
        self.path_mask = f"{snapshot_path}.npz"
        self.path_mcmi = f"{snapshot_path}.mcmi"

    def save_datas(self, plate_image: np.ndarray, mean_colors: dict, mask_info: dict, mask: np.ndarray):
        converted_image = cv2.cvtColor(plate_image, cv2.COLOR_RGB2BGR)
        ic.img_write(self.path_image, converted_image)

        with open(self.path_mean_colors, "w") as mc_file:
            json.dump(mean_colors, mc_file)

        with open(self.path_snapshot_info, "w") as mi_file:
            json.dump(mask_info, mi_file)

        np.savez_compressed(self.path_mask, data=mask)

    def load_datas(self) -> (Image, dict, dict, np.ndarray):
        plate_image = Image().from_path(self.path_image)

        try:
            with open(self.path_mean_colors, "r") as mean_colors_file:
                mean_colors_data = json.load(mean_colors_file)

            with open(self.path_snapshot_info, "r") as mask_info_file:
                snapshot_info_data = json.load(mask_info_file).get("snapshot_info")
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
