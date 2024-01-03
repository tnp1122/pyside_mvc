from enum import Enum


class MaskViewIndex(Enum):
    ORIGIN = 0
    DISTRICT = 1
    MASK = 2


class MaskManagerModel:
    def __init__(self):
        self._current_view = MaskViewIndex.ORIGIN

    @property
    def current_view(self):
        return self._current_view

    @current_view.setter
    def current_view(self, view_index):
        self._current_view = view_index
