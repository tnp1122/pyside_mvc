import cv2
from PySide6.QtCore import QObject, QTimer, Signal

from models.snapshot import Snapshot

WINDOW_NAME = "draw_mask"
MASK_COLOR = (255, 255, 255)
UNMASK_COLOR = (0, 0, 0)


class DrawMask(QObject):
    closed = Signal()

    def __init__(self, snapshot: Snapshot):
        super().__init__()

        self.snapshot = snapshot

        self.drawing = False
        self.removing = False
        self.drawing_thickness = 5
        self.overlay_k = 25
        self.zoom_level = 200

        self.timer_detect_closed = QTimer()
        self.timer_detect_closed.setInterval(100)
        self.timer_detect_closed.timeout.connect(self.detect_closed)

    def open_window(self):
        converted_image = cv2.cvtColor(self.snapshot.mask.mask_filled_array, cv2.COLOR_RGB2BGR)

        height, width, _ = converted_image.shape
        window_width, window_height = 1920 * 0.7, 1080 * 0.7

        if width > height:
            resize_width = window_width
            resize_height = window_width * height / width
        else:
            resize_width = window_height * width / height
            resize_height = window_height

        cv2.namedWindow(WINDOW_NAME, flags=cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(WINDOW_NAME, self.mouse_callback)
        cv2.imshow(WINDOW_NAME, converted_image)
        cv2.resizeWindow(WINDOW_NAME, int(resize_width), int(resize_height))

        self.timer_detect_closed.start()

    def detect_closed(self):
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            self.closed.emit()
            self.timer_detect_closed.stop()

    def mouse_callback(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            cv2.circle(self.snapshot.mask.custom_mask, (x, y), self.drawing_thickness, MASK_COLOR,
                       thickness=cv2.FILLED)
            self.update_overlay(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False

        elif event == cv2.EVENT_RBUTTONDOWN:
            self.removing = True
            cv2.circle(self.snapshot.mask.custom_mask, (x, y), self.drawing_thickness, UNMASK_COLOR,
                       thickness=cv2.FILLED)
            self.update_overlay(x, y)
        elif event == cv2.EVENT_RBUTTONUP:
            self.removing = False

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.circle(self.snapshot.mask.custom_mask, (x, y), self.drawing_thickness, MASK_COLOR,
                           thickness=cv2.FILLED)
                mask_changed = True

            elif self.removing:
                cv2.circle(self.snapshot.mask.custom_mask, (x, y), self.drawing_thickness, UNMASK_COLOR,
                           thickness=cv2.FILLED)
                mask_changed = True
            else:
                mask_changed = False
            self.update_overlay(x, y, mask_changed)

    def update_overlay(self, mouse_x, mouse_y, mask_changed=True):
        mask_info = self.snapshot.mask
        if mask_changed:
            mask_info.on_mask_changed()

        converted_image = cv2.cvtColor(mask_info.mask_filled_array, cv2.COLOR_RGB2BGR)
        height, width, _ = converted_image.shape
        k = self.overlay_k
        crop_x_start = max(0, mouse_x - k)
        crop_y_start = max(0, mouse_y - k)
        crop_x_end = min(width, mouse_x + k)
        crop_y_end = min(height, mouse_y + k)

        crop = converted_image[crop_y_start:crop_y_end, crop_x_start:crop_x_end]
        zoomed_in = cv2.resize(crop, (self.zoom_level, self.zoom_level))

        bound_k = k * 3
        if crop_x_start - bound_k < 0:
            overlay_x_start = 0
            zoomed_x_start = -(crop_x_start - bound_k)
        else:
            overlay_x_start = crop_x_start - bound_k
            zoomed_x_start = 0
        if crop_y_start - bound_k < 0:
            overlay_y_start = 0
            zoomed_y_start = -(crop_y_start - bound_k)
        else:
            overlay_y_start = crop_y_start - bound_k
            zoomed_y_start = 0
        if crop_x_end + bound_k > width:
            overlay_x_end = width
            zoomed_x_end = len(zoomed_in[1]) - (crop_x_end + bound_k - width)
        else:
            overlay_x_end = crop_x_end + bound_k
            zoomed_x_end = len(zoomed_in[1])
        if crop_y_end + bound_k > height:
            overlay_y_end = height
            zoomed_y_end = len(zoomed_in) - (crop_y_end + bound_k - height)
        else:
            overlay_y_end = crop_y_end + bound_k
            zoomed_y_end = len(zoomed_in)

        overlay = converted_image.copy()
        try:
            cropped_zoomed = zoomed_in[zoomed_y_start: zoomed_y_end, zoomed_x_start: zoomed_x_end]
            overlay[overlay_y_start:overlay_y_end, overlay_x_start:overlay_x_end] = cropped_zoomed
        except:
            pass
        cv2.imshow(WINDOW_NAME, overlay)
