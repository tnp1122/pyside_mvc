import numpy as np
from PySide6.QtGui import QImage, QPixmap

from util import image_converter as ic


class Image:
    def __init__(self, array: np.ndarray = None, has_alpha: bool = False):
        self.array = array
        self.has_alpha = has_alpha

    def from_path(self, image_path: str):
        self.array = ic.path_to_nd_array(image_path)
        return self

    @property
    def q_image(self):
        height, width, channel = self.array.shape
        if self.has_alpha:
            bytes_per_line = (width * 24 + 31) // 32 * 4
        else:
            bytes_per_line = width * channel
        return QImage(self.array.data, width, height, bytes_per_line, QImage.Format_RGB888)

    @property
    def q_pixmap(self):
        return QPixmap.fromImage(self.q_image)

    def cropped(self, x, y, width, height):
        return self.array[y:y + height, x:x + width]

    @property
    def shape(self):
        return self.array.shape

    @property
    def has_image(self):
        return self.array is not None
