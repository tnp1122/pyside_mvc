from enum import Enum


class FirstTabIndex(Enum):
    LOGIN = 0
    HOME = 1
    SETTING = 2


class SettingViewIndex(Enum):
    DEFAULT = 0
    CAMERA = 1


class ExperimentTreeIndex(Enum):
    TIMELINE = 0
    SNAPSHOT = 1


class MaskViewIndex(Enum):
    ORIGIN = 0
    DISTRICT = 1
    MASK = 2


class LabCorrectionType(Enum):
    WHOLE_HALL_ROI = 0
    SINGLE_HALL_ROI = 1
    MANUAL_COLOR = 2
