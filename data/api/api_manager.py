import json

from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

from setting_manager import SettingManager


class APIManager:
    BASE_URL = "http://localhost:8000/api/"
    exclude = ["user/login/", "user/regist/"]

    def __init__(self):
        self.manager = QNetworkAccessManager()
        self.setting_manager = SettingManager()

    def _call_api(self, method, endpoint, callback=None, data=None):
        url = QUrl(f"{self.BASE_URL}{endpoint}")
        request = QNetworkRequest(url)

        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        if endpoint not in self.exclude:
            auth = f"Bearer {self.setting_manager.load_access_token()}"
            request.setRawHeader(b"Authorization", auth.encode())

        if method == "GET":
            reply = self.manager.get(request)

        elif method == "POST" and data:
            json_data = json.dumps(data, indent=None, separators=(",", ":"))
            byte_array = QByteArray(json_data.encode())
            reply = self.manager.post(request, byte_array)

        else:
            raise ValueError("Unsupported HTTP method")

        if callback and callable(callback):
            reply.finished.connect(lambda: callback(reply))

    def login(self, login_info, callback):
        endpoint = f"user/login/"
        self._call_api("POST", endpoint, callback, login_info)

    def regist(self, registration_info, callback):
        endpoint = f"user/regist/"
        self._call_api("POST", endpoint, callback, registration_info)

    def get_user_list(self, callback):
        endpoint = f"admin/waiting-users/"
        self._call_api("GET", endpoint, callback)
