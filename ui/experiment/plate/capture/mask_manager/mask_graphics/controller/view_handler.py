class ViewHandler:
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self._border = self.view.scene.border
        self.border.setVisible(False)
        from ui.experiment.plate.capture.mask_manager import MaskViewIndex
        self.set_current_view(MaskViewIndex.ORIGIN)

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    @property
    def border(self):
        return self._border

    def set_current_view(self, index):
        from ui.experiment.plate.capture.mask_manager import MaskViewIndex

        if index == MaskViewIndex.MASK:
            self.view.scene.origin_view.setVisible(False)
            self.view.scene.masking_view.setVisible(True)
            self.border.setVisible(False)
            return

        self.view.scene.origin_view.setVisible(True)
        self.view.scene.masking_view.setVisible(False)
        if index == MaskViewIndex.ORIGIN:
            self.border.setVisible(False)
        elif index == MaskViewIndex.DISTRICT:
            self.border.setVisible(True)
