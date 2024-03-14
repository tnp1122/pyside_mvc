import os

import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap


def img_read(file_path):
    npArr = np.fromfile(file_path, dtype=np.uint8)
    return cv2.imdecode(npArr, cv2.IMREAD_COLOR)


def img_write(file_path, img, params=None):
    try:
        ext = os.path.splitext(file_path)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(file_path, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def path_to_nd_array(image_path: str) -> np.ndarray:
    image = img_read(image_path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def path_to_q_pixmap(image_path: str) -> QPixmap:
    return QPixmap(image_path)


def array_to_q_image(image: np.ndarray, is_toupcam=False) -> QImage:
    height, width, channel = image.shape
    if is_toupcam:
        bytes_per_line = (width * 24 + 31) // 32 * 4
    else:
        bytes_per_line = width * channel
    return QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)


def array_to_q_pixmap(image: np.ndarray, is_toupcam=False) -> QPixmap:
    qimage = array_to_q_image(image, is_toupcam)
    return QPixmap.fromImage(qimage)


def q_pixmap_to_q_image(pixmap: QPixmap) -> QImage:
    return pixmap.toImage()


def q_pixmap_to_array(pixmap: QPixmap) -> np.ndarray:
    image = q_pixmap_to_q_image(pixmap)
    ndarray = np.array(image.bits().asstring(image.byteCount()))
    return ndarray.reshape((image.height(), image.width(), 4))


def get_image_path(image_name):
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


def snapshot_array_to_image_file(image: np.ndarray, snapshot_path: str, image_name: str, file_extension="png") -> str:
    storage_path = os.getenv("LOCAL_STORAGE_PATH")
    directory_path = get_absolute_path(storage_path, snapshot_path)

    file_name = f"{image_name}.{file_extension}"
    image_path = os.path.join(directory_path, file_name)

    converted_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    img_write(image_path, converted_image)

    return image_path


def save_plate_snapshot_image(image: np.ndarray, snapshot_path: str, snapshot_age: int, target_name: str) -> str:
    image_name = f"{snapshot_age}H_{target_name}"
    return snapshot_array_to_image_file(image, snapshot_path, image_name, "png")
