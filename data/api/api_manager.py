import json
import logging
import os

from PySide6.QtCore import QByteArray, QUrl, QThread, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from dotenv import load_dotenv

from ui.common.loading_spinner import LoadingSpinner
from ui.common.toast import Toast
from util.setting_manager import SettingManager

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL")
EXCLUDE_END_POINTS = ["user/login/", "user/regist/"]
REFRESH_TOKEN_END_POINT = "user/refresh/"
METHOD = "[API manager]"
GET = "GET"
POST = "POST"


class APIWorker(QThread):
    finished = Signal(tuple)

    def __init__(self, origin, setting_manager, method, endpoint, callback, body=None, parent=None):
        super().__init__(parent)
        self.origin = origin
        self.setting_manager = setting_manager
        self.retry_count = 1

        self.method = method
        self.endpoint = endpoint
        self.callback = callback
        self.body = body

    def run(self):
        self.manager = QNetworkAccessManager()
        self._call_api(self.method, self.endpoint, self.callback, self.body)
        self.exec()

    def _call_api(self, method, endpoint, callback, body=None, origin_api=None):
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

        if callback and callable(callback):
            reply.finished.connect(lambda: self._reply_intercept(reply, method, endpoint, callback, body))
            return

        logging.warning(f"{METHOD} No Callback function, origin_api: {origin_api}")
        self.finished.emit((callback, reply))

    def _reply_intercept(self, reply, method, endpoint, callback, body=None):
        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if endpoint == REFRESH_TOKEN_END_POINT:
            if status_code == 204:
                headers = reply.rawHeaderPairs()
                for header, value in headers:
                    if header == b"Authentication":
                        auth = value.data().decode("utf-8")
                        access_token = auth.split(" ")[1]
                        self.setting_manager.set_access_token(access_token)
                        self._call_api(self.method, self.endpoint, self.callback, self.body)
                        return
                logging.error(f"{METHOD} Failed to refresh token for unexpected reason")
                return

            callback(reply)
            return

        if status_code == 401:
            self.on_auth_failed(reply, method, endpoint, callback, body)
            return

        self.finished.emit((callback, reply))

    def on_auth_failed(self, reply, method, endpoint, callback, body=None):
        self.retry_count -= 1
        if self.retry_count < 0:
            self.finished.emit((callback, reply))
            return

        endpoint = REFRESH_TOKEN_END_POINT
        url = QUrl(f"{BASE_URL}{endpoint}")
        auth = f"Bearer {self.setting_manager.get_refresh_token()}"

        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        request.setRawHeader(b"Authorization", auth.encode())

        json_data = json.dumps({}, indent=None, separators=(",", ":"))
        byte_array = QByteArray(json_data.encode())
        reply = self.manager.post(request, byte_array)

        reply.finished.connect(lambda: self._reply_intercept(reply, method, endpoint, callback, body))


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
            self.spinner = LoadingSpinner()

    def _call_api(self, method, endpoint, callback, body=None, origin_api=None):
        self.start_loading()

        log = f"API Call [{method}] {endpoint} || callback: {callback} == body:{body} || origin: {origin_api}"
        logging.info(log)
        worker = APIWorker(self, self.setting_manager, method, endpoint, callback, body)
        worker.finished.connect(lambda args: self.end_loading(args, worker))
        worker.start()

    def start_loading(self):
        if not self.spinner:
            self.spinner = LoadingSpinner()
        self.spinner.start_loading()

    def end_loading(self, args, worker):
        if self.spinner:
            self.spinner.end_loading()
        worker.quit()
        worker.deleteLater()

        try:
            callback = args[0]
            reply = args[1]
            callback(reply)
            reply.deleteLater()
        except:
            logging.error("API 호출 실패")

    def on_failure(self, reply):
        json_str = reply.readAll().data().decode("utf-8")
        try:
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

        except:
            try:
                msg = json.loads(json_str)["message"]
            except:
                msg = reply.errorString()
        finally:
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
        endpoint = self.METAL + "sample/"
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
        endpoint = self.ADDITIVE + "sample/"
        self._call_api(POST, endpoint, callback, additive_samples)

    """ ### solvent ### """

    def get_solvents(self, callback):
        endpoint = self.SOLVENT
        self._call_api(GET, endpoint, callback)

    def add_solvents(self, callback, solvents):
        endpoint = self.SOLVENT
        self._call_api(POST, endpoint, callback, solvents)

    """ experiment """
    EXPERIMENT = "experiment/"

    def get_experiments(self, callback):
        endpoint = self.EXPERIMENT
        self._call_api(GET, endpoint, callback)

    def get_experiment_tree(self, callback):
        endpoint = self.EXPERIMENT + "tree/"
        self._call_api(GET, endpoint, callback)

    def add_experiment(self, callback, experiment):
        endpoint = self.EXPERIMENT
        self._call_api(POST, endpoint, callback, experiment)

    def remove_experiment(self, callback, experiment_id):
        endpoint = self.EXPERIMENT + f"{experiment_id}/remove/"
        self._call_api(POST, endpoint, callback)

    def get_targets(self, callback, experiment_id):
        endpoint = self.EXPERIMENT + f"{experiment_id}/target/"
        self._call_api(GET, endpoint, callback)

    def add_targets(self, callback, experiment_id, targets):
        endpoint = self.EXPERIMENT + f"{experiment_id}/target/"
        self._call_api(POST, endpoint, callback, targets)

    """ sensor """

    def get_sensor_combinations(self, callback, experiment_id):
        endpoint = self.EXPERIMENT + f"{experiment_id}/sensor-combination/"
        self._call_api(GET, endpoint, callback)

    def get_sensor_combination(self, callback, combination_id):
        endpoint = self.EXPERIMENT + f"1/sensor-combination/{combination_id}/"
        self._call_api(GET, endpoint, callback)

    def add_sensor_combination(self, callback, experiment_id, sensor_combination):
        endpoint = self.EXPERIMENT + f"{experiment_id}/sensor-combination/"
        self._call_api(POST, endpoint, callback, sensor_combination)

    def remove_sensor_combination(self, callback, experiment_id, combination_id):
        endpoint = self.EXPERIMENT + f"{experiment_id}/sensor-combination/{combination_id}/remove/"
        self._call_api(POST, endpoint, callback)

    """ plate """
    PLATE = "plate/"

    def add_plate(self, callback, plate):
        endpoint = self.PLATE
        self._call_api(POST, endpoint, callback, plate)

    def remove_plate(self, callback, plate_id):
        endpoint = self.PLATE + f"{plate_id}/remove/"
        self._call_api(POST, endpoint, callback)

    def add_snapshot(self, callback, plate_id, snapshot):
        endpoint = self.PLATE + f"{plate_id}/snapshot/"
        self._call_api(POST, endpoint, callback, snapshot)

    def get_snapshot(self, callback, plate_id, snapshot_id):
        endpoint = self.PLATE + f"{plate_id}/snapshot/{snapshot_id}/"
        self._call_api(GET, endpoint, callback)

    def remove_snapshot(self, callback, plate_id, snapshot_id):
        endpoint = self.PLATE + f"{plate_id}/snapshot/{snapshot_id}/remove/"
        self._call_api(POST, endpoint, callback)

    """ timeline """
    TIMELINE = "timeline/"

    def add_timeline(self, callback, timeline):
        endpoint = self.TIMELINE
        self._call_api(POST, endpoint, callback, timeline)

    def get_timeline(self, callback, timeline_id):
        endpoint = self.TIMELINE + f"{timeline_id}/"
        self._call_api(GET, endpoint, callback)

    def remove_timeline(self, callback, timeline_id):
        endpoint = self.TIMELINE + f"{timeline_id}/remove/"
        self._call_api(POST, endpoint, callback)
