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


def array_to_q_image(image: np.ndarray, has_alpha=False) -> QImage:
    image = np.ascontiguousarray(image)
    height, width, channel = image.shape
    if has_alpha:
        bytes_per_line = (width * 24 + 31) // 32 * 4
    else:
        bytes_per_line = width * channel
    return QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)


def array_to_q_pixmap(image: np.ndarray, has_alpha=False) -> QPixmap:
    qimage = array_to_q_image(image, has_alpha)
    return QPixmap.fromImage(qimage)


def q_pixmap_to_q_image(pixmap: QPixmap) -> QImage:
    return pixmap.toImage()


def q_pixmap_to_array(pixmap: QPixmap) -> np.ndarray:
    image = q_pixmap_to_q_image(pixmap)
    ndarray = np.array(image.bits().asstring(image.byteCount()))
    return ndarray.reshape((image.height(), image.width(), 4))
