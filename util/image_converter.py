import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap


def path_to_nd_array(image_path: str) -> np.ndarray:
    image = cv2.imread(image_path)
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
