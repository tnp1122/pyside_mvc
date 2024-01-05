import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage, QPixmap

WINDOW_NAME = "masking"
MASK_COLOR = (0, 0, 0)
UNMASK_COLOR = (255, 255, 255)


class Masking(QObject):
    masked_image_updated_signal = Signal()

    def __init__(self, origin_image):
        super().__init__()
        self.origin_image = cv2.imread(origin_image)

        self.circle_mask = np.zeros_like(self.origin_image[:, :, :], dtype=np.uint8)
        self.flare_mask = np.ones_like(self.origin_image[:, :, :], dtype=np.uint8)
        self.custom_mask = np.full_like(self.origin_image[:, :, :], 255, dtype=np.uint8)

        self.masked_array = np.ma.masked_array(self.origin_image, cv2.bitwise_not(self.circle_mask))
        self.mask_filled_image = self.masked_array.filled(0).astype(np.uint8)

        self.drawing = False
        self.removing = False
        self.drawing_thickness = 5
        self.overlay_k = 25
        self.zoom_level = 200

        self.set_flare_mask()

    def mouse_callback(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            cv2.circle(self.custom_mask, (x, y), self.drawing_thickness, MASK_COLOR, thickness=cv2.FILLED)
            print(f"{x}, {y}: {self.custom_mask[y][x]}")
            self.update_overlay(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.removing = True
            cv2.circle(self.custom_mask, (x, y), self.drawing_thickness, UNMASK_COLOR, thickness=cv2.FILLED)
            print(f"{x}, {y}: {self.custom_mask[y][x]}")
            self.update_overlay(x, y)
        elif event == cv2.EVENT_RBUTTONUP:
            self.removing = False

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.circle(self.custom_mask, (x, y), self.drawing_thickness, MASK_COLOR, thickness=cv2.FILLED)
                mask_changed = True
            elif self.removing:
                cv2.circle(self.custom_mask, (x, y), self.drawing_thickness, UNMASK_COLOR, thickness=cv2.FILLED)
                mask_changed = True
            else:
                mask_changed = False
            self.update_overlay(x, y, mask_changed)

    def update_overlay(self, mouse_x, mouse_y, mask_changed=True):
        if mask_changed:
            circle_masked_array = np.ma.masked_array(self.origin_image, cv2.bitwise_not(self.circle_mask))
            flare_masked_array = np.ma.masked_array(circle_masked_array, cv2.bitwise_not(self.flare_mask))
            self.masked_array = np.ma.masked_array(flare_masked_array, cv2.bitwise_not(self.custom_mask))
            self.mask_filled_image = self.masked_array.filled(0).astype(np.uint8)
        height, width, _ = self.mask_filled_image.shape
        k = self.overlay_k
        x_start = max(0, mouse_x - k)
        y_start = max(0, mouse_y - k)
        x_end = min(width, mouse_x + k)
        y_end = min(height, mouse_y + k)

        bound_k = k * 3
        if x_start < bound_k or y_start < bound_k or x_end > width - bound_k or y_end > height - bound_k:
            cv2.imshow(WINDOW_NAME, self.mask_filled_image)
            return

        crop = self.mask_filled_image[y_start:y_end, x_start:x_end]
        zoomed_in = cv2.resize(crop, (self.zoom_level, self.zoom_level))

        overlay = self.mask_filled_image.copy()
        overlay[y_start - k * 3:y_end + k * 3, x_start - k * 3:x_end + k * 3] = zoomed_in

        if mask_changed:
            self.masked_image_updated_signal.emit()
        cv2.imshow(WINDOW_NAME, overlay)

    def show_image(self):
        # masked_array에 마스킹은 표현되어 있지만 이미지로 보기 위해 마스킹을 검은색으로 채움

        height, width, _ = self.mask_filled_image.shape
        window_width, window_height = 1920 * 0.8, 1080 * 0.8
        if width > height:
            resize_width = window_width
            resize_height = window_width * height / width
        else:
            resize_width = window_height * width / height
            resize_height = window_height

        cv2.namedWindow(WINDOW_NAME, flags=cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(WINDOW_NAME, self.mouse_callback)
        cv2.imshow(WINDOW_NAME, self.mask_filled_image)
        cv2.resizeWindow(WINDOW_NAME, int(resize_width), int(resize_height))

    def get_pixmap(self):
        # cv2용 이미지와 QPixmap용 색 배열이 달라 변환이 필요함
        converted_image = cv2.cvtColor(self.mask_filled_image, cv2.COLOR_BGR2RGB)

        height, width, channel = converted_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(converted_image, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        return pixmap

    def mask(self):
        circle_masked_array = np.ma.masked_array(self.origin_image, cv2.bitwise_not(self.circle_mask))
        flare_masked_array = np.ma.masked_array(circle_masked_array, cv2.bitwise_not(self.flare_mask))
        self.masked_array = np.ma.masked_array(flare_masked_array, cv2.bitwise_not(self.custom_mask))
        self.mask_filled_image = self.masked_array.filled(0).astype(np.uint8)
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
                cv2.circle(self.circle_mask, (int(x + x_axis), int(y + y_axis)), radius, UNMASK_COLOR,
                           thickness=cv2.FILLED)
        self.mask()

    def set_flare_mask(self, thresh=200):
        _, flare_mask = cv2.threshold(self.origin_image, thresh, 255, cv2.THRESH_BINARY_INV)
        temp = np.all(flare_mask[:, :] == [255, 255, 255], axis=-1)
        flare_mask[~temp] = [0, 0, 0]

        self.flare_mask = flare_mask
        self.mask()
