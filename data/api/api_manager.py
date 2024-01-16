import inspect
import json
import logging
import os

from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from dotenv import load_dotenv

from util.setting_manager import SettingManager

load_dotenv()

BASE_URL = os.getenv("LOCAL_BASE_URL")
EXCLUDE_END_POINTS = ["user/login/", "user/regist/"]
REFRESH_TOKEN_END_POINT = "user/refresh/"
METHOD = "[API manager]"
GET = "GET"
POST = "POST"


class APIManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(APIManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.manager = QNetworkAccessManager()
            self.setting_manager = SettingManager()

    def _call_api(self, method, endpoint, callback=None, data=None, origin_api=None):
        url = QUrl(f"{BASE_URL}{endpoint}")
        request = QNetworkRequest(url)

        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        if endpoint == REFRESH_TOKEN_END_POINT:
            auth = f"Bearer {self.setting_manager.get_refresh_token()}"
        elif endpoint not in EXCLUDE_END_POINTS:
            auth = f"Bearer {self.setting_manager.get_access_token()}"
        else:
            auth = ""
        request.setRawHeader(b"Authorization", auth.encode())

        if method == GET:
            reply = self.manager.get(request)

        elif method == POST:
            if not data:
                data = {}
            json_data = json.dumps(data, indent=None, separators=(",", ":"))
            byte_array = QByteArray(json_data.encode())
            reply = self.manager.post(request, byte_array)

        else:
            raise ValueError("Unsupported HTTP method")

        if endpoint == REFRESH_TOKEN_END_POINT:
            reply.finished.connect(lambda: self._reply_check(origin_api, reply, method, endpoint, callback, data))
            return

        if callback and callable(callback):
            origin_api = inspect.currentframe().f_back.f_code.co_name
            reply.finished.connect(lambda: self._reply_check(origin_api, reply, method, endpoint, callback, data))
            return

        logging.warning(f"{METHOD} No Callback function, origin_api: {origin_api}")

    def _reply_check(self, origin_api, reply, method, endpoint, callback=None, data=None):
        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if endpoint == REFRESH_TOKEN_END_POINT:
            if status_code == 200:
                headers = reply.rawHeaderPairs()
                for header, value in headers:
                    if header == b"Authentication":
                        auth = value.data().decode("utf-8")
                        access_token = auth.split(" ")[1]
                        self.setting_manager.set_access_token(access_token)
                        origin = getattr(self, origin_api)
                        if data:
                            origin(data, callback)
                        else:
                            origin(callback)
                        return
                logging.error(f"{METHOD} Failed to refresh token for unexpected reason")
                return

            callback(reply)
            return

        if status_code == 401:
            self.refresh_token(callback, origin_api)
            return

        callback(reply)

    def regist(self, registration_info, callback):
        endpoint = f"user/regist/"
        self._call_api(POST, endpoint, callback, registration_info)

    def login(self, login_info, callback):
        endpoint = f"user/login/"
        self._call_api(POST, endpoint, callback, login_info)

    def refresh_token(self, callback, origin_api):
        endpoint = REFRESH_TOKEN_END_POINT
        self._call_api(POST, endpoint, callback=callback, origin_api=origin_api)

    def get_user_info(self, callback):
        endpoint = f"user/info/"
        self._call_api(GET, endpoint, callback)

    def get_user_list(self, callback):
        endpoint = f"admin/waiting-users/"
        self._call_api(GET, endpoint, callback)
