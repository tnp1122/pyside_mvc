import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage, QPixmap

WINDOW_NAME = "masking"


class Masking(QObject):
    masked_image_updated_signal = Signal()

    def __init__(self, origin_image):
        super().__init__()
        self.origin_image = cv2.imread(origin_image)

        self.circle_mask = np.zeros_like(self.origin_image[:, :, :], dtype=np.uint8)
        self.flare_mask = np.ones_like(self.origin_image[:, :, :], dtype=np.uint8)

        self.masked_array = np.ma.masked_array(self.origin_image, cv2.bitwise_not(self.circle_mask))

        self.set_flare_mask()

    def show_image(self):
        # masked_array에 마스킹은 표현되어 있지만 이미지로 보기 위해 마스킹을 검은색으로 채움
        mask_filled_image = self.masked_array.filled(0).astype(np.uint8)

        height, width, _ = mask_filled_image.shape
        window_width, window_height = 1920 * 0.8, 1080 * 0.8
        if width > height:
            resize_width = window_width
            resize_height = window_width * height / width
        else:
            resize_width = window_height * width / height
            resize_height = window_height

        cv2.namedWindow(WINDOW_NAME, flags=cv2.WINDOW_NORMAL)
        cv2.imshow(WINDOW_NAME, mask_filled_image)
        cv2.resizeWindow(WINDOW_NAME, int(resize_width), int(resize_height))

    def get_pixmap(self):
        # cv2용 이미지와 QPixmap용 색 배열이 달라 변환이 필요함
        mask_filled_image = self.masked_array.filled(0).astype(np.uint8)
        converted_image = cv2.cvtColor(mask_filled_image, cv2.COLOR_BGR2RGB)

        height, width, channel = converted_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(converted_image, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        return pixmap

    def mask(self):
        circle_masked_array = np.ma.masked_array(self.origin_image, cv2.bitwise_not(self.circle_mask))
        self.masked_array = np.ma.masked_array(circle_masked_array, cv2.bitwise_not(self.flare_mask))
        self.masked_image_updated_signal.emit()

    def set_circle_mask(self, mask_info):
        self.circle_mask = np.zeros_like(self.origin_image[:, :, :], dtype=np.uint8)
        x = mask_info["x"]
        y = mask_info["y"]
        radius = mask_info["radius"]

        if mask_info["direction"] == 0:
            vertical_axes = mask_info["additive_axes"]
            horizontal_axes = mask_info["solvent_axes"]
        else:
            vertical_axes = mask_info["solvent_axes"]
            horizontal_axes = mask_info["additive_axes"]

        for y_axis in horizontal_axes:
            for x_axis in vertical_axes:
                cv2.circle(self.circle_mask, (int(x + x_axis), int(y + y_axis)), radius, (255, 255, 255),
                           thickness=cv2.FILLED)
        self.mask()

    def set_flare_mask(self, thresh=200):
        _, flare_mask = cv2.threshold(self.origin_image, thresh, 255, cv2.THRESH_BINARY_INV)
        temp = np.all(flare_mask[:, :] == [255, 255, 255], axis=-1)
        flare_mask[~temp] = [0, 0, 0]

        self.flare_mask = flare_mask
        self.mask()
