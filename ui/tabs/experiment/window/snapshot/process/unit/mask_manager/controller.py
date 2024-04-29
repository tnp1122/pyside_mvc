from model.snapshot import Snapshot
from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager import MaskManagerView, MaskManagerModel
from util import image_converter as ic


class MaskManagerController(BaseController):
    def __init__(self, parent=None, snapshot: Snapshot = None):
        self.snapshot = snapshot

        super().__init__(MaskManagerModel, MaskManagerView, parent, snapshot)
        view: MaskManagerView = self.view
        view.btn_confirm.clicked.connect(self.close)

    def close(self):
        self.snapshot.on_processed()
        super().close()


def main():
    from PySide6.QtWidgets import QApplication
    import os

    app = QApplication([])
    image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../plate_image.jpg")
    image = ic.path_to_nd_array(image_path)
    widget = MaskManagerController(origin_image=image)
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
