import json

from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest


class APIManager:
    BASE_URL = "http://localhost:8000/api/"

    def __init__(self):
        self.manager = QNetworkAccessManager()

    def _call_api(self, method, endpoint, data=None, callback=None):
        url = QUrl(f"{self.BASE_URL}{endpoint}")
        request = QNetworkRequest(url)
        request.setRawHeader(b"Authorization", "access_token".encode())

        if method == "POST" and data:
            request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
            json_data = json.dumps(data, indent=None, separators=(",", ":"))
            byte_array = QByteArray(json_data.encode())
            reply = self.manager.post(request, byte_array)
            # reply.setProperty("api_endpoint", endpoint)

            if callback and callable(callback):
                reply.finished.connect(lambda: callback(reply))
            # return reply
        else:
            raise ValueError("Unsupported HTTP method")

    def login(self, login_info, callback=None):
        endpoint = f"user/login/"
        self._call_api("POST", endpoint, login_info, callback)

        # if callback:
        #     callback(reply)

    def regist(self, registration_info, callback=None):
        endpoint = f"user/regist/"
        self._call_api("POST", endpoint, registration_info, callback)
