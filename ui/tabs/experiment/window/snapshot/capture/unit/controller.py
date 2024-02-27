import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap
from numpy import ndarray

from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.capture.unit import PlateCaptureUnitModel, PlateCaptureUnitView
from ui.tabs.experiment.window.snapshot.capture.unit.mask_manager import Masking, MaskGraphicsController, \
    MaskManagerController


class PlateCaptureUnitController(BaseController):
    def __init__(self, parent=None):
        super().__init__(PlateCaptureUnitModel, PlateCaptureUnitView, parent)

        self.masked_array: ndarray
        self.mask_info = {}
        self.mean_colors = []
        self.mean_colored_pixmap = QPixmap()
        self.cropped_original_pixmap = QPixmap()

        view: PlateCaptureUnitView = self.view
        view.mask_manager_apply_clicked.connect(self.on_mask_apply_clicked)

    def close(self):
        self.masked_array = None
        self.mask_info = None
        self.mean_colors = None
        self.mean_colored_pixmap = None
        self.cropped_original_pixmap = None

        super().close()

    def init_controller(self):
        super().init_controller()

    def set_image_size(self, width=None, height=None):
        self.view.set_image_size(width, height)

    def set_selected(self, is_selected):
        self.view.set_selected(is_selected)

    def on_mask_apply_clicked(self):
        # mask_info: 이미지 크롭 용
        # masked_array: 색 추출 용
        # 크롭된 마스크드 이미지: 유닛 라벨 설정용
        mask_manager: MaskManagerController = self.view.mask_manager
        masking: Masking = mask_manager.view.masking
        graphics: MaskGraphicsController = mask_manager.view.graphics

        # 데이터 참조
        self.mask_info = graphics.get_circle_mask_info()
        info = self.mask_info
        x = info["x"]
        y = info["y"]
        r = info["radius"]
        if info["direction"] == 0:
            width, height = info["width"], info["height"]
            cols, rows = info["additive_axes"], info["solvent_axes"]
        else:
            width, height = info["height"], info["width"]
            cols, rows = info["solvent_axes"], info["additive_axes"]

        # 마스킹 데이터 저장
        self.masked_array = masking.masked_array
        np.savez_compressed('compressed_data.npz', self.masked_array.mask)

        # 픽스맵 생성
        self.make_mean_colored_pixmap(x, y, r, width, height, cols, rows)
        self.make_cropped_original_pixmap(x, y, width, height)

        masked_pixmap = masking.get_pixmap()
        self.view.set_masked_pixmap(masked_pixmap, x, y, width, height)

        mask_manager.close()

    def make_mean_colored_pixmap(self, x, y, r, width, height, cols, rows):
        masked_image: np.ma.masked_array = self.masked_array
        cropped_image = masked_image[y:y + height, x:x + width]

        # 색 평균 계산
        self.mean_colors = []
        for j, cy in enumerate(rows):
            self.mean_colors.append([])
            for cx in cols:
                x1, x2 = int(cx - r), int(cx + r)
                y1, y2 = int(cy - r), int(cy + r)
                cell = cropped_image[y1:y2, x1:x2]
                mean_R = np.mean(cell[:, :, 0])
                mean_G = np.mean(cell[:, :, 1])
                mean_B = np.mean(cell[:, :, 2])
                mean_color = [mean_R, mean_G, mean_B]
                self.mean_colors[j].append(mean_color)

        # 색 평균 원 그리기
        new_image = np.zeros_like(cropped_image[:, :, :], dtype=np.uint8)
        for j, cy in enumerate(rows):
            for i, cx in enumerate(cols):
                mean_color = self.mean_colors[j][i]
                cv2.circle(new_image, (int(cx), int(cy)), r, mean_color, thickness=cv2.FILLED)

        # 픽스맵 생성
        converted_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        height, width, channel = converted_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(converted_image, width, height, bytes_per_line, QImage.Format_RGB888)
        self.mean_colored_pixmap = QPixmap.fromImage(q_image)

        return self.mean_colored_pixmap

    def make_cropped_original_pixmap(self, x, y, width, height):
        view: PlateCaptureUnitView = self.view
        self.cropped_original_pixmap = view.pixmap.copy(x, y, width, height)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = PlateCaptureUnitController()
    widget.view.set_image_size(300, 500)
    widget.view.set_no_image()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
