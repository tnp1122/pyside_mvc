from model import Image
from model.snapshot import Snapshot
from ui.common import BaseController
from ui.tabs.experiment.window.snapshot.process.unit import ProcessUnitModel, ProcessUnitView


class ProcessUnitController(BaseController):
    def __init__(self, parent=None, snapshot: Snapshot = None):
        super().__init__(ProcessUnitModel, ProcessUnitView, parent, snapshot)

        self.capture_id = None
        self.snapshot = snapshot

    def init_controller(self):
        super().init_controller()

    def set_image_size(self, width=None, height=None):
        view: ProcessUnitView = self.view
        view.set_image_size(width, height)

    def set_selected(self, is_selected):
        view: ProcessUnitView = self.view
        view.set_selected(is_selected)

    def set_snapshot_image(self, image: Image):
        self.snapshot.init_origin_image(image)


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
