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


def get_local_storage_path(snapshot_path, snapshot_age, target_name, type: str = "png") -> str:
    capture_name = f"{snapshot_age}H_{target_name}"
    file_name = f"{capture_name}.{type}"
    storage_path = os.getenv("LOCAL_STORAGE_PATH")
    directory_path = get_absolute_path(storage_path, snapshot_path)

    return os.path.join(directory_path, file_name)


def save_plate_snapshot_image(image: np.ndarray, snapshot_path: str, snapshot_age: int, target_name: str) -> str:
    image_path = get_local_storage_path(snapshot_path, snapshot_age, target_name, "png")

    converted_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    ic.img_write(image_path, converted_image)


def save_mean_color_mask_info(mcmi: dict, snapshot_path, snapshot_age, target_name):
    mcmi_path = get_local_storage_path(snapshot_path, snapshot_age, target_name, "mcmi")

    with open(mcmi_path, "w") as mcmi_file:
        json.dump(mcmi, mcmi_file)


def save_mask(mask: np.ndarray, snapshot_path, snapshot_age, target_name):
    mask_path = get_local_storage_path(snapshot_path, snapshot_age, target_name, "npz")
    np.savez_compressed(mask_path, data=mask)


def load_plate_snapshot_image(snapshot_path: str, snapshot_age: int, target_name: str) -> np.ndarray:
    image_path = get_local_storage_path(snapshot_path, snapshot_age, target_name, "png")
    return Image().from_path(image_path)


def load_mean_color_mask_info(snapshot_path: str, snapshot_age: int, target_name: str) -> dict:
    mcmi_path = get_local_storage_path(snapshot_path, snapshot_age, target_name, "mcmi")

    with open(mcmi_path, "r") as mcmi_file:
        mcmi = json.load(mcmi_file)

    if mcmi:
        return mcmi
    else:
        return None


def load_mask(snapshot_path: str, snapshot_age: int, target_name: str):
    mask_path = get_local_storage_path(snapshot_path, snapshot_age, target_name, "npz")
    return np.load(mask_path)["data"]


class SnapshotDataManager:
    def __init__(self, snapshot_path: str, snapshot_age: int, target_name: str):
        self.snapshot_path = snapshot_path
        self.snapshot_age = snapshot_age
        self.target_name = target_name

    def save_datas(self, cropped_image, mcmi, mask):
        save_plate_snapshot_image(cropped_image, self.snapshot_path, self.snapshot_age, self.target_name)
        save_mean_color_mask_info(mcmi, self.snapshot_path, self.snapshot_age, self.target_name)
        save_mask(mask, self.snapshot_path, self.snapshot_age, self.target_name)

    def load_datas(self) -> (Image, dict, np.ndarray):
        snapshot_image = load_plate_snapshot_image(self.snapshot_path, self.snapshot_age, self.target_name)
        mcmi = load_mean_color_mask_info(self.snapshot_path, self.snapshot_age, self.target_name)
        mask = load_mask(self.snapshot_path, self.snapshot_age, self.target_name)

        return snapshot_image, mcmi, mask
