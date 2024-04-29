from util.enums import MaskViewIndex


class ViewHandler:
    def __init__(self, view):
        self.view = view
        self.area = self.view.scene.area

        self.area.setVisible(False)
        self.set_current_view(MaskViewIndex.ORIGIN)

    def close(self):
        self.view = None
        self.area = None

    def set_current_view(self, index):
        if index == MaskViewIndex.MASK:
            self.view.scene.origin_view.setVisible(False)
            self.view.scene.masking_view.setVisible(True)
            self.area.setVisible(False)
            return

        self.view.scene.origin_view.setVisible(True)
        self.view.scene.masking_view.setVisible(False)
        if index == MaskViewIndex.ORIGIN:
            self.area.setVisible(False)
        elif index == MaskViewIndex.DISTRICT:
            self.area.setVisible(True)
