from util.enums import MaskViewIndex


class MaskManagerModel:
    def __init__(self):
        self._current_view = MaskViewIndex.ORIGIN

    @property
    def current_view(self):
        return self._current_view

    @current_view.setter
    def current_view(self, view_index):
        self._current_view = view_index
