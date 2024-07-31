from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QFrame, QCheckBox

from models.snapshot import Snapshot, Timeline
from ui.common import BaseWidgetView, ImageButton, SetCamera, ColoredButton
from ui.common.image_viewer import ImageViewerController
from ui.tabs.experiment.window.timeline import PlateTimelineModel
from ui.tabs.experiment.window.timeline.widgets.color_graph import ColorGraphController
from ui.tabs.experiment.window.timeline.widgets.interval_config import IntervalConfig
from ui.tabs.experiment.window.timeline.widgets.select_combination_table import SelectCombinationTableController
from util import local_storage_manager as lsm
from util.colors import EXCEL_GREEN


class PlateTimelineView(BaseWidgetView):
    width_et_box = 35
    width_combo_box = 48
    height_et = 24

    def __init__(self, parent=None, combination_id=None):
        self.combination_id = combination_id
        self.model: PlateTimelineModel = None
        self.snapshot_instance: Snapshot = None

        super().__init__(parent)

    def set_model(self, model: PlateTimelineModel):
        self.model = model
        self.snapshot_instance: Snapshot = model.snapshot_instance

    def init_view(self):
        super().init_view()

        # 카메라 설정
        set_camera = SetCamera()
        """ 컨텐츠 """
        # 카메라 뷰
        image_viewer_args = {"mode": 1, "snapshot_instance": self.snapshot_instance}
        self.image_viewer = ImageViewerController(args=image_viewer_args)
        image_path = lsm.get_static_image_path("cogwheel.png")
        cogwheel = QPixmap(image_path)
        self.lb_interval_info = QLabel()
        self.btn_interval_config = ImageButton(cogwheel)
        self.btn_interval_config.clicked.connect(self.show_interval_config)
        lyt_interval_info = QHBoxLayout()
        lyt_interval_info.addWidget(self.lb_interval_info, 0, alignment=Qt.AlignLeft)
        lyt_interval_info.addWidget(self.btn_interval_config, 0, alignment=Qt.AlignRight)

        self.lb_camera_setting = QLabel()
        self.lb_camera_setting.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        lyt_main_content = QVBoxLayout()
        lyt_main_content.setContentsMargins(10, 0, 10, 0)
        lyt_main_content.addStretch()
        lyt_main_content.addWidget(self.image_viewer.view)
        lyt_main_content.addLayout(lyt_interval_info)
        lyt_main_content.addWidget(self.lb_camera_setting)
        lyt_main_content.addStretch()

        # 그래프
        self.graph = ColorGraphController()

        # 조합 선택
        self.btn_export_to_excel = ColoredButton("엑셀로 저장", background_color=EXCEL_GREEN)
        self.cb_hide_velocity = QCheckBox("Velocity 숨기기")
        self.combination_table = SelectCombinationTableController(combination_id=self.combination_id)
        lyt_combination = QVBoxLayout()
        lyt_combination.setContentsMargins(0, 0, 0, 0)
        lyt_combination.addWidget(self.cb_hide_velocity)
        lyt_combination.addWidget(self.btn_export_to_excel)
        lyt_combination.addWidget(self.combination_table.view)

        # 컨텐츠 컨테이너
        lyt_content = QHBoxLayout()
        lyt_content.setContentsMargins(0, 0, 0, 0)
        lyt_content.addWidget(set_camera)
        lyt_content.addLayout(lyt_main_content)
        lyt_content.addWidget(self.graph.view)
        lyt_content.addLayout(lyt_combination)

        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        divider1.setFrameShadow(QFrame.Sunken)
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setFrameShadow(QFrame.Sunken)

        """ 전체 컨테이너 """
        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(1, 1, 1, 1)
        lyt.setSpacing(5)
        lyt.addLayout(lyt_content)

    def update_lb_interval_info(self):
        timeline: Timeline = self.model.timeline

        if timeline.current_count >= timeline.end_count:
            info_str = "타임라인 촬영 완료"
        else:
            current_round = timeline.current_round
            total_round = timeline.total_round
            current_interval = timeline.current_interval
            count = timeline.count_of_current_round
            total_count = timeline.total_count_of_current_round

            info_str = (f"[{total_round}라운드 중 {current_round + 1}라운드 (촬영 주기: {current_interval}초)] "
                        f"{count}/{total_count}")

        self.lb_interval_info.setText(info_str)

    def show_interval_config(self):
        timeline: Timeline = self.model.timeline
        widget_config = IntervalConfig(timeline["rounds"])
        widget_config.closed.connect(self.update_lb_interval_info)

        widget_config.exec()

    def update_lb_camera_settings(self):
        model: PlateTimelineModel = self.model
        settings = model.camera_settings
        str_auto_expo = "수동 노출" if settings["auto_expo"] == 0 else "자동 노출"
        af_index = settings["anti_flicker_index"]
        if af_index == 0:
            str_anti_flicker = "교류 전류(60Hz)"
        elif af_index == 1:
            str_anti_flicker = "교류 전류(50Hz)"
        else:
            str_anti_flicker = "직류(DC)"

        lb_contents = f"""[마스크 Threshold] {model.snapshot_instance.mask.flare_threshold}
[해상도] {settings["resolution"]}
[{str_auto_expo}] 타겟: {settings["expo_target"]}, 노출 시간: {round(settings["expo_time"], 3)}ms, 게인: {settings["expo_gain"]}%
[화이트 밸런스] 색 온도: {settings["wb_temp"]}, 색조: {settings["wb_tint"]}
[블랙 밸런스] 빨강: {settings["bb_r"]}, 녹색: {settings["bb_g"]}, 파랑: {settings["bb_b"]}  
[색 조정] 색상 {settings["saturation"]}, 채도: {settings["brightness"]}, 밝기: {settings["brightness"]}, 명암: {settings["contrast"]}, 감마: {settings["gamma"]}
[광원 주파수] {str_anti_flicker}
        """
        self.lb_camera_setting.setText(lb_contents)
