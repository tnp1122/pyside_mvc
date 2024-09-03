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
            # raise CameraUnitError("카메라를 인식하지 못했습니다.")
            msg = "카메라를 인식하지 못했습니다."
            logging.error(msg)
            Toast().toast(msg)
            return

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
        if self.direction % 2 == 0:
            img = np.frombuffer(self.pData, dtype=np.uint8).reshape((self.imgHeight, self.imgWidth, 3))
        else:
            img = np.frombuffer(self.pData, dtype=np.uint8).reshape((self.imgWidth, self.imgHeight, 3))
        return img

    @property
    def resolutions(self):
        resolution = []
        for i in range(self.cur.model.preview):
            resolution.append((self.cur.model.res[i].width, self.cur.model.res[i].height))

        return resolution

    @property
    def rgb(self):
        if self.cam:
            return self.cam.get_BlackBalance()
        return [0, 0, 0]

    def rotate_direction(self):
        self.direction = (self.direction + 1) % 4

    def set_rotate(self, index):
        self.direction = index % 4
        self.cam.put_Option(toupcam.TOUPCAM_OPTION_ROTATE, index % 4 * 90)

    def set_resolution(self, index):
        if self.cam:
            self.cam.Stop()

        self.res = index
        self.imgWidth = self.cur.model.res[index].width
        self.imgHeight = self.cur.model.res[index].height

        if self.cam:
            self.cam.put_eSize(self.res)
            self.start_camera()

    def _execute_if_cam(self, func, *args, **kwargs):
        if self.cam:
            func(*args, **kwargs)
            return True
        return False

    """ 노출 및 게인"""

    def _get_min_auto_expo_time_a_gain(self):
        if self.cam:
            return self.cam.get_MinAutoExpoTimeAGain()
        return [None, None]

    def _get_max_auto_expo_time_a_gain(self):
        if self.cam:
            return self.cam.get_MaxAutoExpoTimeAGain()
        return [None, None]

    def get_expo_time_range(self):
        if self.cam:
            min_expo_time = self._get_min_auto_expo_time_a_gain()[0]
            max_expo_time = self._get_max_auto_expo_time_a_gain()[0]
            return min_expo_time, max_expo_time
        return None, None

    def get_expo_gain_range(self):
        if self.cam:
            min_expo_time = self._get_min_auto_expo_time_a_gain()[1]
            max_expo_time = self._get_max_auto_expo_time_a_gain()[1]
            return min_expo_time, max_expo_time
        return None, None


    def set_auto_expo(self, state):
        return self._execute_if_cam(self.cam.put_AutoExpoEnable, 1 if state else 0)

    def set_expo_target(self, value):
        return self._execute_if_cam(self._set_expo_target, value)

    def _set_expo_target(self, value):
        if self.cam.get_AutoExpoEnable() == 1:  # 노출 타겟은 자동일 때 작동함
            self.cam.put_AutoExpoTarget(value)

    def set_expo_time(self, value):
        return self._execute_if_cam(self._set_expo_time, value)

    def _set_expo_time(self, value):
        if self.cam.get_AutoExpoEnable() != 1:
            self.cam.put_ExpoTime(value)

    def set_expo_gain(self, value):
        return self._execute_if_cam(self._set_expo_gain, value)

    def _set_expo_gain(self, value):
        if self.cam.get_AutoExpoEnable() != 1:
            self.cam.put_ExpoAGain(value)

    """ 화이트 밸런스 """

    def init_white_balance(self):
        return self._execute_if_cam(self._init_white_balance)

    def _init_white_balance(self):
        self.cam.put_TempTint(toupcam.TOUPCAM_TEMP_DEF, toupcam.TOUPCAM_TINT_DEF)

    def auto_white_balance_once(self):
        return self._execute_if_cam(self.cam.AwbOnce)

    def set_white_balance_temp(self, value):
        self.temp = value
        return self._execute_if_cam(self.cam.put_TempTint, self.temp, self.tint)

    def set_white_balance_tint(self, value):
        self.tint = value
        return self._execute_if_cam(self.cam.put_TempTint, self.temp, self.tint)

    def set_white_balance_gain(self, rgb):
        return self._execute_if_cam(self._set_white_balance_gain, rgb)

    def _set_white_balance_gain(self, rgb):
        tt = self.cam.Gain2TempTint(rgb)
        print(f"[_set_white_balance_gain] rgb: {rgb}, g2tt: {tt}")
        self.cam.put_TempTint(*self.cam.Gain2TempTint(rgb))

    def get_white_balance_gain(self):
        tt = self.cam.get_TempTint()
        g = self.cam.TempTint2Gain(*self.cam.get_TempTint())
        print(f"[get_white_balance_gain] tt: {tt}, tt2g: {g}")
        if self.cam:
            return self.cam.TempTint2Gain(*self.cam.get_TempTint())

    """ 블랙 밸런스 """

    def auto_black_blance_once(self):
        return self._execute_if_cam(self.cam.AbbOnce)

    def set_black_balance(self, color_index: int, value: int):
        rgb = list(self.rgb)
        rgb[color_index] = value
        return self._execute_if_cam(self.cam.put_BlackBalance, rgb)

    def init_black_balance(self):
        return self._execute_if_cam(self.cam.put_BlackBalance, (0, 0, 0))

    """ 색 조정 """

    def set_hue(self, value):
        return self._execute_if_cam(self.cam.put_Hue, value)

    def set_saturation(self, value):
        return self._execute_if_cam(self.cam.put_Saturation, value)

    def set_brightness(self, value):
        return self._execute_if_cam(self.cam.put_Brightness, value)

    def set_contrast(self, value):
        return self._execute_if_cam(self.cam.put_Contrast, value)

    def set_gamma(self, value):
        return self._execute_if_cam(self.cam.put_Gamma, value)

    def init_color(self):
        return self._execute_if_cam(self._init_color)

    def _init_color(self):
        hue = toupcam.TOUPCAM_HUE_DEF
        saturation = toupcam.TOUPCAM_SATURATION_DEF
        brightness = toupcam.TOUPCAM_BRIGHTNESS_DEF
        contrast = toupcam.TOUPCAM_CONTRAST_DEF
        gamma = toupcam.TOUPCAM_GAMMA_DEF
        self.cam.put_Hue(hue)
        self.cam.put_Saturation(saturation)
        self.cam.put_Brightness(brightness)
        self.cam.put_Contrast(contrast)
        self.cam.put_Gamma(gamma)
