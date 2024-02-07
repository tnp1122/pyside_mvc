import json
import logging

from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QWidget, QHBoxLayout

from data.api.api_manager import APIManager
from ui.common import BaseTabWidgetView, BaseController, ColoredButton, BaseWidgetView
from ui.common.toast import Toast


class SensorBaseTabModel:
    def __init__(self):
        pass


class SensorBaseTabView(BaseTabWidgetView):
    btn_margin = (-10, -10)

    def __init__(self, parent=None, subject_name=None):
        super().__init__(parent)
        self.sample = BaseController(SensorBaseTabModel, BaseWidgetView)
        self.subject = BaseController(SensorBaseTabModel, BaseWidgetView)
        # 상속받는 컨트롤러에서 sample 및 tables 테이블 선언

        if subject_name == "metal":
            sample_name, subject_name = "금속 시료", "금속 종류"
        elif subject_name == "additive":
            sample_name, subject_name = "첨가제 시료", "첨가제 종류"
        else:
            sample_name, subject_name = "", "용매 종류"
        self.sample_tab_name = sample_name
        self.subject_tab_name = subject_name

    def init_view(self):
        super().init_view()

        self.addTab(self.sample.view, self.sample_tab_name)
        self.addTab(self.subject.view, self.subject_tab_name)
        if self.sample_tab_name == "":
            self.setTabEnabled(0, False)
            self.setTabVisible(0, False)

        self.btn_cancel = ColoredButton("취소", background_color="gray")
        self.btn_save = ColoredButton("저장", background_color="red")
        self.btns = QWidget(self)
        lyt = QHBoxLayout(self.btns)
        lyt.addWidget(self.btn_cancel)
        lyt.addWidget(self.btn_save)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_floating_widget_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_floating_widget_position()

    def update_floating_widget_position(self):
        window_width, window_height = self.width(), self.height()

        btns_x = window_width - self.btns.width() - self.btn_margin[0]
        btnx_y = self.btn_margin[1]

        self.btns.move(btns_x, btnx_y)

    def set_sample_table_items(self, sample_items):
        self.sample.set_table_items(sample_items)

    def set_subject_table_items(self, subject_items):
        if self.sample_tab_name != "":
            self.sample.update_subject(subject_items)
        self.subject.set_table_items(subject_items)


class SensorBaseTabController(BaseController):
    api_manager = APIManager()
    samples = []
    subjects = []

    def __init__(self, parent=None, subject_name=None):

        self.subject_name = subject_name
        super().__init__(SensorBaseTabModel, SensorBaseTabView, parent, subject_name)

    def init_controller(self):
        super().init_controller()

        if self.subject_name != "solvent":
            self.update_sample_items()
        self.update_subject_items()

        self.view.btn_cancel.clicked.connect(self.on_cancel_clicked)
        self.view.btn_save.clicked.connect(self.on_save_clicked)

    def get_id_from_name(self, items, name):
        for item in items:
            if item["name"] == name:
                return item["id"]
        return -1

    def update_sample_items(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.samples = json.loads(json_str)[self.subject_name + "_samples"]
                self.view.set_sample_table_items(self.samples)
            else:
                self.api_manager.on_failure(reply)

        if self.subject_name == "metal":
            self.api_manager.get_metal_samples(api_handler)
        else:
            self.api_manager.get_additive_samples(api_handler)

    def update_subject_items(self):
        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                json_str = reply.readAll().data().decode("utf-8")
                self.subjects = json.loads(json_str)[self.subject_name + "s"]
                self.view.set_subject_table_items(self.subjects)
            else:
                self.api_manager.on_failure(reply)

        if self.subject_name == "metal":
            self.api_manager.get_metals(api_handler)
        elif self.subject_name == "additive":
            self.api_manager.get_additives(api_handler)
        else:
            self.api_manager.get_solvents(api_handler)

    def on_cancel_clicked(self):
        index = self.view.currentIndex()
        if index == 0:
            self.view.sample.cancel_added_items()
        else:
            self.view.subject.cancel_added_items()

    def on_save_clicked(self):
        index = self.view.currentIndex()
        if index == 0:
            self.save_new_sample()
        else:
            self.save_new_subject()

    def save_new_sample(self):
        new_samples = self.view.sample.get_new_items()
        for sample in new_samples:
            sample[self.subject_name] = self.get_id_from_name(self.subjects, sample[self.subject_name])

        key = self.subject_name + "_samples"
        body = {key: new_samples}

        if not body[key]:
            return

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                self.update_sample_items()
            else:
                self.api_manager.on_failure(reply)

        if self.subject_name == "metal":
            self.api_manager.add_metal_samples(api_handler, body)
        else:
            self.api_manager.add_additive_samples(api_handler, body)

    def save_new_subject(self):
        new_subjects = [s.strip() for s in self.view.subject.get_new_items() if s.strip()]

        key = self.subject_name + "s"
        body = {key: [{"name": subject} for subject in new_subjects]}

        if not body[key]:
            return

        def api_handler(reply):
            if reply.error() == QNetworkReply.NoError:
                self.update_subject_items()
            else:
                self.api_manager.on_failure(reply)

        if self.subject_name == "metal":
            self.api_manager.add_metals(api_handler, body)
        elif self.subject_name == "additive":
            self.api_manager.add_additives(api_handler, body)
        else:
            self.api_manager.add_solvents(api_handler, body)
