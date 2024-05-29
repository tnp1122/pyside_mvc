import logging
import sys

import numpy as np
from PySide6.QtCore import Signal, QObject

from ui.common.toast import Toast
from util.camera_manager import toupcam


class CameraUnitError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class CameraManager(QObject):
    _instance = None
    signal_image = Signal(np.ndarray)

    def __new__(cls, parent=None):
        if not cls._instance:
            cls._instance = super(CameraManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if not hasattr(self, "initialized"):
            if parent is not None:
                super().__init__()

                logging.info("init Camera Manager")
                self.initialized = True

                self.camera_unit = CameraUnit(parent)
                self.camera_unit.open_camera()
                self.camera_unit.signal_image.connect(self.signal_image.emit)

    def get_current_image(self):
        if hasattr(self, "camera_unit") and self.camera_unit is not None:
            unit: CameraUnit = self.camera_unit
            return unit.current_image
        return None

    def set_direction(self):
        self.rotate_direction()

    def rotate_direction(self):
        unit: CameraUnit = self.camera_unit
        unit.rotate_direction()


class CameraUnit(QObject):
    _instance = None

    evtCallback = Signal(int)

    video_started = Signal(bool)
    signal_image = Signal(np.ndarray)
    direction = 1

    def __new__(cls, parent=None):
        if not cls._instance:
            cls._instance = super(CameraUnit, cls).__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if not hasattr(self, "initialized"):
            if parent is not None:
                super().__init__()

                logging.info("init Camera Unit")

                self.cam = None
                self.imgWidth = 0
                self.imgHeight = 0
                self.pData = None
                self.res = 0
                self.temp = toupcam.TOUPCAM_TEMP_DEF
                self.tint = toupcam.TOUPCAM_TINT_DEF

                self.initialized = True
                self.evtCallback.connect(self.onevtCallback)

    def close_camera(self):
        if self.cam:
            self.cam.Close()
        self.cam = None
        self.pData = None

    def open_camera(self):
        logging.info("open Camera Unit")
        arr = toupcam.Toupcam.EnumV2()
        if len(arr) == 0:
            raise CameraUnitError("카메라를 인식하지 못했습니다.")

        self.cur = arr[0]
        self.cam = toupcam.Toupcam.Open(self.cur.id)
        if self.cam:
            self.res = self.cam.get_eSize()
            self.imgWidth = self.cur.model.res[self.res].width
            self.imgHeight = self.cur.model.res[self.res].height
            self.cam.put_Option(toupcam.TOUPCAM_OPTION_BYTEORDER, 0)
            self.cam.put_AutoExpoEnable(1)
            self.start_camera()

    def start_camera(self):
        self.pData = bytes(toupcam.TDIBWIDTHBYTES(self.imgWidth * 24) * self.imgHeight)
        try:
            self.cam.StartPullModeWithCallback(self.eventCallBack, self)
        except toupcam.HRESULTException:
            self.close_camera()
            raise CameraUnitError("이미지를 받아오는데 실패했습니다.")
        else:
            self.video_started.emit(True)

    @staticmethod
    def eventCallBack(nEvent, self):
        '''callbacks come from toupcam.dll/so internal threads, so we use qt signal to post this event to the UI thread'''
        self.evtCallback.emit(nEvent)

    def onevtCallback(self, nEvent):
        '''this run in the UI thread'''
        if self.cam:
            if toupcam.TOUPCAM_EVENT_IMAGE == nEvent:
                self.handleImageEvent()

    def handleImageEvent(self):
        try:
            self.cam.PullImageV3(self.pData, 0, 24, 0, None)
        except toupcam.HRESULTException:
            pass
        else:
            self.signal_image.emit(self.current_image)

    @property
    def current_image(self):
        img = np.frombuffer(self.pData, dtype=np.uint8).reshape((self.imgHeight, self.imgWidth, 3))
        img = np.rot90(img, k=-self.direction)
        return np.ascontiguousarray(img)

    @property
    def resolutions(self):
        resolution = []
        for i in range(self.cur.model.preview):
            resolution.append((self.cur.model.res[i].width, self.cur.model.res[i].height))

        return resolution

    def rotate_direction(self):
        self.direction = (self.direction + 1) % 4

    def set_resolution(self, index):
        if self.cam:
            self.cam.Stop()

        self.res = index
        self.imgWidth = self.cur.model.res[index].width
        self.imgHeight = self.cur.model.res[index].height

        if self.cam:
            self.cam.put_eSize(self.res)
            self.start_camera()

    def set_auto_expo(self, state):
        if self.cam:
            self.cam.put_AutoExpoEnable(1 if state else 0)
            return True
        return False

    def set_expo_time(self, value):
        if self.cam:
            if self.cam.get_AutoExpoEnable() != 1:
                self.cam.put_ExpoTime(value)
            return True
        return False

    def set_expo_gain(self, value):
        if self.cam:
            if self.cam.get_AutoExpoEnable() != 1:
                self.cam.put_ExpoAGain(value)
            return True
        return False

    def set_auto_WB(self):
        if self.cam:
            self.cam.AwbOnce()
            return True
        return False

    def set_WB_temp(self, value):
        if self.cam:
            self.temp = value
            self.cam.put_TempTint(self.temp, self.tint)
            return True
        return False

    def set_WB_tint(self, value):
        if self.cam:
            self.tint = value
            self.cam.put_TempTint(self.temp, self.tint)
            return True
        return False
