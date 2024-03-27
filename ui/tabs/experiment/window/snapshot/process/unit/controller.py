import cv2
import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap

from model import Image
from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.process.unit import ProcessUnitModel, ProcessUnitView
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import Masking, MaskGraphicsController, \
    MaskManagerController
from util import image_converter as ic


class ProcessUnitController(BaseController):
    mask_applied = Signal()
    mask_info_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(ProcessUnitModel, ProcessUnitView, parent)

        self.masked_array = None
        self.transformed_mask_info = {}
        self.mean_colors = []
        self.mean_colored_pixmap = QPixmap()
        self.cropped_original_pixmap = QPixmap()

        self.capture_id = None

        view: ProcessUnitView = self.view
        view.mask_manager_apply_clicked.connect(self.on_mask_apply_clicked)
        view.clear_mask_info.connect(self.clear_mask_info)

    def close(self):
        self.clear_mask_info()

        super().close()

    def clear_mask_info(self):
        self.masked_array = None
        self.transformed_mask_info = None
        self.mean_colors = None
        self.mean_colored_pixmap = None
        self.cropped_original_pixmap = None
        self.mask_info_cleared.emit()

    def init_controller(self):
        super().init_controller()

    def set_image_size(self, width=None, height=None):
        self.view.set_image_size(width, height)

    def set_selected(self, is_selected):
        self.view.set_selected(is_selected)

    def set_image(self, image: Image):
        self.clear_mask_info()
        view: ProcessUnitView = self.view
        view.set_image(image)

    def on_mask_apply_clicked(self):
        # mask_info: 이미지 크롭 용
        # masked_array: 색 추출 용
        # 크롭된 마스크드 이미지: 유닛 라벨 설정용
        mask_manager: MaskManagerController = self.view.mask_manager
        masking: Masking = mask_manager.view.masking
        graphics: MaskGraphicsController = mask_manager.view.graphics

        # 데이터 참조
        mask_info = graphics.get_circle_mask_info()
        masking.set_circle_mask(mask_info)
        self.masked_array = masking.masked_array
        self.transformed_mask_info = graphics.get_transformed_mask_info()

        graphics.save_circle_mask_info()
        mask_manager.close()

        self.apply_mask_info()

    def apply_mask_info(self):
        info = self.transformed_mask_info
        x, y, r, width, height, cols, rows = (info[key] for key in ["x", "y", "r", "width", "height", "cols", "rows"])

        # 픽스맵 생성
        self.make_mean_colored_pixmap(x, y, r, width, height, cols, rows)
        self.make_cropped_original_pixmap(x, y, width, height)

        masked_pixmap = ic.array_to_q_pixmap(self.masked_array.filled(0).astype(np.uint8))
        self.view.set_masked_pixmap(masked_pixmap, x, y, width, height)

        self.mask_applied.emit()

    def make_mean_colored_pixmap(self, x, y, r, width, height, cols, rows):
        masked_array: np.ma.masked_array = self.masked_array
        cropped_array = masked_array[y:y + height, x:x + width]

        # 색 평균 계산
        self.mean_colors = []
        for j, cy in enumerate(rows):
            self.mean_colors.append([])
            for cx in cols:
                x1, x2 = int(cx - r), int(cx + r)
                y1, y2 = int(cy - r), int(cy + r)
                cell = cropped_array[y1:y2, x1:x2]
                mean_color = np.mean(cell, axis=(0, 1))
                self.mean_colors[j].append(mean_color)

        # 색 평균 원 그리기
        new_array = np.zeros_like(cropped_array[:, :, :], dtype=np.uint8)
        for j, cy in enumerate(rows):
            for i, cx in enumerate(cols):
                mean_color = self.mean_colors[j][i]
                try:
                    cv2.circle(new_array, (int(cx), int(cy)), r, mean_color, thickness=cv2.FILLED)
                except:
                    pass

        self.mean_colored_pixmap = ic.array_to_q_pixmap(new_array)

        return self.mean_colored_pixmap

    def make_cropped_original_pixmap(self, x, y, width, height):
        view: ProcessUnitView = self.view
        self.cropped_original_pixmap = view.pixmap.copy(x, y, width, height)

    def set_snapshot_datas(self, cropped_image: Image, mean_color_mask_info: dict, mask: np.ndarray):
        self.set_image(cropped_image)
        self.mean_colors = mean_color_mask_info["mean_colors"]
        self.transformed_mask_info = mean_color_mask_info["mask_info"]
        self.masked_array = np.ma.masked_array(self.view.origin_image.array, mask)

        self.apply_mask_info()

    def get_snapshot_datas(self):
        info = self.transformed_mask_info
        x, y, width, height = (info[key] for key in ["x", "y", "width", "height"])

        view: ProcessUnitView = self.view
        cropped_image = view.origin_image.cropped(x, y, width, height)
        cropped_mask_info = self.transformed_mask_info.copy()
        cropped_mask_info["x"], cropped_mask_info["y"] = 0, 0

        mean_color_mask_info = {"mean_colors": self.mean_colors, "mask_info": cropped_mask_info}
        mask = self.masked_array[y:y + height, x:x + width].mask

        return cropped_image, mean_color_mask_info, mask


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ProcessUnitController()
    widget.view.set_image_size(300, 500)
    widget.view.set_no_image()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
