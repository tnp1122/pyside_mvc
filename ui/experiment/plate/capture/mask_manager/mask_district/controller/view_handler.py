class ViewHandler:
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self._border = self.view.scene.border
        self.border.setVisible(False)

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

        if index == MaskViewIndex.ORIGIN:
            self.border.setVisible(False)
        elif index == MaskViewIndex.DISTRICT:
            self.border.setVisible(True)
        else:
            self.border.setVisible(False)
