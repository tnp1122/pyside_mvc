import numpy as np
from PySide6.QtCore import QTimer

from models.snapshot import Snapshot, Timeline
from ui.common import BaseController
from ui.common.camera_widget.section_camera_display import SectionCameraDisplay
from ui.common.loading_spinner import with_loading_spinner
from ui.common.toast import Toast
from ui.tabs.experiment.window.snapshot.difference.excel_manager import TimelineExcelWorker
from ui.tabs.experiment.window.timeline import PlateTimelineModel, PlateTimelineView
from ui.tabs.experiment.window.timeline.widgets.color_graph import ColorGraphController
from ui.tabs.experiment.window.timeline.widgets.select_combination_table import SelectCombinationTableController


class PlateTimelineController(BaseController):
    def __init__(self, parent=None, args=None):
        combination_id = args["combination_id"]
        super().__init__(PlateTimelineModel, PlateTimelineView, parent, combination_id)

        self.target = args["target"]
        self.timeline_path = args["timeline_path"]
        self.association_indexes = []
        self.velocity_visibility = True

        model: PlateTimelineModel = self.model
        model.init_timeline_instance(self.timeline_path, self.target.name)

        view: PlateTimelineView = self.view
        view.update_lb_interval_info()
        view.camera_widget.camera_display.lb_camera.snapshot_initialized_signal.connect(self.load_timeline)
        view.cb_apply_lab_correction.stateChanged.connect(self.update_graph)
        view.cb_hide_velocity.clicked.connect(self.on_velocity_visibility_changed)
        view.btn_export_to_excel.clicked.connect(self.export_to_excel)

        combination_table: SelectCombinationTableController = view.combination_table
        combination_table.display_associations_changed.connect(self.on_associations_changed)

    def init_controller(self):
        model: PlateTimelineModel = self.model
        view: PlateTimelineView = self.view
        section_camera_display = view.camera_widget.camera_display
        view.set_model(model)

        super().init_controller()

        view.btn_run_timeline.clicked.connect(self.on_run_timeline_clicked)

        section_camera_display.lab_correction_factors_set_signal.connect(self.on_lab_correction_factors_set)

    @with_loading_spinner
    def export_to_excel(self):
        timeline: Timeline = self.model.timeline
        apply_lab_correct = self.view.cb_apply_lab_correction.isChecked()
        elapsed_times, rgb_datas, distance_datas = timeline.get_timeline_datas(self.association_indexes,
                                                                               apply_lab_correct)

        worker = TimelineExcelWorker(elapsed_times, rgb_datas, distance_datas, self.timeline_path, self)
        worker.finished.connect(self.on_excel_saved)
        worker.start()
        return worker

    def on_excel_saved(self, _, success):
        if success:
            message = f"저장 완료: {self.timeline_path}_distance_datas.csv"
        else:
            message = "저장 실패"
        Toast().toast(message, duration=6000)

    @with_loading_spinner
    def load_timeline(self):
        model: PlateTimelineModel = self.model
        view: PlateTimelineView = self.view
        timeline: Timeline = model.timeline
        snapshot_instance: Snapshot = view.camera_widget.status.snapshot_instance

        worker, camera_settings = timeline.load_timeline(snapshot_instance)
        if worker is not None:
            worker.finished.connect(self.on_timeline_loaded)
            worker.start()
        if camera_settings is not None:
            model.camera_settings.update(camera_settings)
            view.update_lb_camera_settings()

        return worker

    def update_graph(self):
        view: PlateTimelineView = self.view
        color_graph: ColorGraphController = view.graph
        timeline: Timeline = self.model.timeline
        apply_lab_correct = view.cb_apply_lab_correction.isChecked()

        color_graph.update_graph(
            *timeline.get_datas(self.association_indexes, apply_lab_correct, self.velocity_visibility))

    def on_timeline_loaded(self):
        view: PlateTimelineView = self.view
        self.update_graph()
        view.update_lb_interval_info()

    def set_enabled_cb_apply_lab_correction(self, enabled):
        view: PlateTimelineView = self.view
        view.cb_apply_lab_correction.setEnabled(enabled)
        view.cb_apply_lab_correction.setChecked(enabled)

    def on_lab_correction_factors_set(self, lab_correction_factors: np.ndarray):
        view: PlateTimelineView = self.view
        snapshot_instance: Snapshot = view.camera_widget.status.snapshot_instance
        timeline: Timeline = self.model.timeline

        # if snapshot_instance.lab_correction_factors is not None:
        self.set_enabled_cb_apply_lab_correction(True)
        timeline.update_lab_correction_factors(lab_correction_factors)
        self.update_graph()

    def on_associations_changed(self, association_indexes: list):
        color_graph: ColorGraphController = self.view.graph
        graph_colors = color_graph.set_colors(len(association_indexes))

        camera_display: SectionCameraDisplay = self.view.camera_widget.camera_display
        camera_display.set_sensor_indexes(association_indexes, graph_colors)
        self.association_indexes = association_indexes
        self.update_graph()

    def on_velocity_visibility_changed(self, state):
        self.velocity_visibility = not state
        self.update_graph()

    def on_run_timeline_clicked(self):
        view: PlateTimelineView = self.view
        model: PlateTimelineModel = self.model
        model.is_running = not model.is_running

        view.cb_apply_lab_correction.setEnabled(not model.is_running)
        view.switch_btn_run_timeline(model.is_running)

        if model.is_running:
            model.get_camera_setting()
            view.update_lb_camera_settings()

            timeline: Timeline = model.timeline
            timeline.init_plate_info(view.camera_widget.snapshot_instance)
            QTimer.singleShot(0, self.take_snapshot)

    def take_snapshot(self):
        if not self.model.is_running:
            return

        view: PlateTimelineView = self.view
        camera_display: SectionCameraDisplay = view.camera_widget.camera_display

        model: PlateTimelineModel = self.model
        timeline: Timeline = model.timeline
        # snapshot_instance: Snapshot = camera_display.status.snapshot_instance

        if timeline.current_count >= timeline.end_count:
            model.is_running = False
            view.switch_btn_run_timeline(False)
            view.update_lb_interval_info()
            return

        QTimer.singleShot(timeline.current_interval * 1000, self.take_snapshot)

        snapshot_instance = camera_display.take_snapshot()
        view.update_lb_interval_info()
        timeline.append_snapshot(snapshot_instance)

        self.update_graph()


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = PlateTimelineController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
