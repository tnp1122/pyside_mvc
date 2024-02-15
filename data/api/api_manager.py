import inspect
import json
import logging
import os

from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from dotenv import load_dotenv

from ui.common.toast import Toast
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

    def _call_api(self, method, endpoint, callback, body=None, origin_api=None):
        log = f"API Call [{method}] {endpoint} || callback: {callback} == body:{body} || origin: {origin_api}"
        logging.info(log)

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
            if not body:
                body = {}
            json_data = json.dumps(body, indent=None, separators=(",", ":"))
            byte_array = QByteArray(json_data.encode())
            reply = self.manager.post(request, byte_array)

        else:
            raise ValueError("Unsupported HTTP method")

        if endpoint == REFRESH_TOKEN_END_POINT:
            reply.finished.connect(lambda: self._reply_intercept(origin_api, reply, endpoint, callback, body))
            return

        if callback and callable(callback):
            origin_api = inspect.currentframe().f_back.f_code.co_name
            reply.finished.connect(lambda: self._reply_intercept(origin_api, reply, endpoint, callback, body))
            return

        logging.warning(f"{METHOD} No Callback function, origin_api: {origin_api}")

    def _reply_intercept(self, origin_api, reply, endpoint, callback, body=None):
        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if endpoint == REFRESH_TOKEN_END_POINT:
            if status_code == 204:
                headers = reply.rawHeaderPairs()
                for header, value in headers:
                    if header == b"Authentication":
                        auth = value.data().decode("utf-8")
                        access_token = auth.split(" ")[1]
                        self.setting_manager.set_access_token(access_token)
                        origin = getattr(self, origin_api)
                        if body:
                            origin(callback, body)
                        else:
                            origin(callback)
                        return
                logging.error(f"{METHOD} Failed to refresh token for unexpected reason")
                return

            callback(reply)
            return

        if status_code == 401:
            self.refresh_token(callback, body, origin_api)
            return

        callback(reply)

    def on_failure(self, reply):
        try:
            json_str = reply.readAll().data().decode("utf-8")
            error_body = json.loads(json_str)["message"]
            code = error_body["code"]
            if code == "required" or code == "null" or code == "empty":
                msg = "누락된 항목이 있습니다."
            elif code == "unique":
                msg = "중복된 항목이 있습니다."
            elif code == "not_a_list":
                msg = "로직 에러"
            elif code == "max_length":
                msg = "입력 가능한 길이를 초과했습니다."
            elif code == "min_length":
                msg = "길이가 너무 짧습니다."
            elif code == "not_found":
                msg = "상위 객체를 찾지 못 했습니다."
            else:
                msg = f"{error_body}"

            logging.error(msg)
            Toast().toast(msg)

        except:
            msg = reply.errorString()

            logging.error(msg)
            Toast().toast(msg)

    """ user """

    def regist(self, callback, registration_info):
        endpoint = "user/regist/"
        self._call_api(POST, endpoint, callback, registration_info)

    def login(self, callback, login_info):
        endpoint = "user/login/"
        self._call_api(POST, endpoint, callback, login_info)

    def refresh_token(self, callback, body, origin_api):
        endpoint = REFRESH_TOKEN_END_POINT
        self._call_api(POST, endpoint, callback, body, origin_api)

    def get_user_info(self, callback):
        endpoint = "user/info/"
        self._call_api(GET, endpoint, callback)

    """ admin """

    def get_user_list(self, callback):
        endpoint = "admin/waiting-users/"
        self._call_api(GET, endpoint, callback)

    def approve_user(self, callback, result, user_id):
        endpoint = f"admin/approve-user/{user_id}"
        self._call_api(POST, endpoint, callback, result)

    """ experiment """

    def get_experiments(self, callback):
        endpoint = "experiment/"
        self._call_api(GET, endpoint, callback)

    def add_experiment(self, callback, experiment):
        endpoint = "experiment/"
        self._call_api(POST, endpoint, callback, experiment)

    def get_targets(self, callback, experiment_id):
        endpoint = f"experiment/{experiment_id}/target/"
        self._call_api(GET, endpoint, callback)

    def add_targets(self, callback, experiment_id, targets):
        endpoint = f"experiment/{experiment_id}/target/"
        self._call_api(POST, endpoint, callback, targets)

    """ material """
    METAL = "material/metal/"
    ADDITIVE = "material/additive/"
    SOLVENT = "material/solvent/"

    """ ### metal ### """

    def get_metals(self, callback):
        endpoint = self.METAL
        self._call_api(GET, endpoint, callback)

    def add_metals(self, callback, metals):
        endpoint = self.METAL
        self._call_api(POST, endpoint, callback, metals)

    def get_metal_samples(self, callback):
        endpoint = self.METAL + "sample/"
        self._call_api(GET, endpoint, callback)

    def add_metal_samples(self, callback, metal_samples):
        endpoint = self.METAL + f"sample/"
        self._call_api(POST, endpoint, callback, metal_samples)

    """ ### additive ### """

    def get_additives(self, callback):
        endpoint = self.ADDITIVE
        self._call_api(GET, endpoint, callback)

    def add_additives(self, callback, additives):
        endpoint = self.ADDITIVE
        self._call_api(POST, endpoint, callback, additives)

    def get_additive_samples(self, callback):
        endpoint = self.ADDITIVE + "sample/"
        self._call_api(GET, endpoint, callback)

    def add_additive_samples(self, callback, additive_samples):
        endpoint = self.ADDITIVE + f"sample/"
        self._call_api(POST, endpoint, callback, additive_samples)

    """ ### solvent ### """

    def get_solvents(self, callback):
        endpoint = self.SOLVENT
        self._call_api(GET, endpoint, callback)

    def add_solvents(self, callback, solvents):
        endpoint = self.SOLVENT
        self._call_api(POST, endpoint, callback, solvents)
