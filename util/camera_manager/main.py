import logging
import sys

import numpy as np
from PySide6.QtCore import Signal, QObject

from ui.common.toast import Toast
from util.camera_manager import toupcam


class CanNotFindDeviceError(Exception):
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

                self.initialized = True
                self.camera_unit = CameraUnit()

                self.connect_to_camera()

    def connect_to_camera(self):
        logging.info("connect to camera")
        if self.camera_unit:
            self.camera_unit.close()
            self.camera_unit = None

        toupcams = toupcam.Toupcam.EnumV2()
        for cam in toupcams:
            try:
                self.camera_unit = CameraUnit(cam.displayname, cam.id, cam.model)
                break
            except Exception as e:
                msg = f"카메라 연결 실패: {e}"
                Toast().toast(msg)
                logging.warning(msg)

        if self.camera_unit:
            try:
                self.camera_unit.connect_to_camera()
            except Exception as e:
                msg = f"카메라 연결 실패: {e}"
                Toast().toast(msg)
                logging.error(msg)

            self.camera_unit.signal_image.connect(lambda img: self.signal_image.emit(img))

    def get_current_image(self):
        if self.camera_unit:
            unit: CameraUnit = self.camera_unit
            image = unit.get_current_image()

            return image
        return None

    def set_direction(self):
        unit: CameraUnit = self.camera_unit
        unit.set_direction()


class CameraUnit(QObject):
    signal_image = Signal(np.ndarray)
    direction = 1

    def __init__(self, name=None, cam_id=None, model=None):
        super().__init__()
        self.name = name
        self.cam_id = cam_id
        self.model = model
        self.cam = None
        self.buf = None
        self.width = 0
        self.height = 0

    def close(self):
        if self.cam is not None:
            self.cam.Close()
            self.cam = None
        self.deleteLater()

    def connect_to_camera(self):
        try:
            if toupcam.Toupcam.Replug(self.cam_id) > 0:
                self.cam = toupcam.Toupcam.Open(self.cam_id)
            else:
                raise CanNotFindDeviceError("카메라 연결 상태를 확인하세요.")
        except Exception as e:
            raise e

        self.width, self.height = self.cam.get_Size()
        bufsize = ((self.width * 24 + 31) // 32 * 4) * self.height
        self.buf = bytes(bufsize)

        if sys.platform == "win32":
            self.cam.put_Option(toupcam.TOUPCAM_OPTION_BYTEORDER, 0)
            self.cam.StartPullModeWithCallback(self.cameraCallback, self)

    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            try:
                ctx.cam.PullImageV2(ctx.buf, 24, None)
            except toupcam.HRESULTException as e:
                ctx.exception.emit(f"pull image failed: {e}")
            else:
                img_np = ctx.get_current_image()
                ctx.signal_image.emit(img_np)

    def get_current_image(self):
        image = np.frombuffer(self.buf, dtype=np.uint8).reshape((self.height, self.width, 3))
        image = np.rot90(image, k=-self.direction)
        image = np.ascontiguousarray(image)
        return image

    def set_direction(self):
        self.direction = (self.direction + 1) % 4
