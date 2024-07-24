from PySide6.QtCore import QTimer

from models.snapshot import Snapshot, Timeline
from ui.common import BaseController
from ui.common.image_viewer import ImageViewerController
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
        view.image_viewer.instance_initialized.connect(self.load_timeline)
        view.cb_hide_velocity.clicked.connect(self.on_velocity_visibility_changed)
        view.btn_export_to_excel.clicked.connect(self.export_to_excel)

        combination_table: SelectCombinationTableController = view.combination_table
        combination_table.display_associations_changed.connect(self.on_associations_changed)

    def init_controller(self):
        model: PlateTimelineModel = self.model
        self.view.set_model(model)

        super().init_controller()

        image_viewer: ImageViewerController = self.view.image_viewer
        image_viewer.run_timeline_clicked.connect(self.on_run_timeline_clicked)

    @with_loading_spinner
    def export_to_excel(self):
        timeline: Timeline = self.model.timeline
        elapsed_times, rgb_datas, distance_datas = timeline.get_timeline_datas(self.association_indexes)

        worker = TimelineExcelWorker(elapsed_times, rgb_datas, distance_datas, self.timeline_path, self)
        worker.finished.connect(self.on_excel_saved)
        worker.start()
        return worker

    def on_excel_saved(self, _, success):
        if success:
            message = f"저장 완료: {self.timeline_path}.xlsx"
        else:
            message = "저장 실패"
        Toast().toast(message, duration=6000)

    @with_loading_spinner
    def load_timeline(self):
        model: PlateTimelineModel = self.model
        view: PlateTimelineView = self.view
        timeline: Timeline = model.timeline

        worker, camera_settings = timeline.load_timeline(model.snapshot_instance)
        if worker is not None:
            worker.finished.connect(self.on_timeline_loaded)
            worker.start()
        if camera_settings is not None:
            model.camera_settings.update(camera_settings)
            view.update_lb_camera_settings()

        return worker

    def update_graph(self):
        color_graph: ColorGraphController = self.view.graph
        timeline: Timeline = self.model.timeline

        color_graph.update_graph(*timeline.get_datas(self.association_indexes, self.velocity_visibility))

    def on_timeline_loaded(self):
        view: PlateTimelineView = self.view
        self.update_graph()
        view.update_lb_interval_info()

    def on_associations_changed(self, association_indexes: list):
        color_graph: ColorGraphController = self.view.graph
        graph_colors = color_graph.set_colors(len(association_indexes))

        image_viewer: ImageViewerController = self.view.image_viewer
        image_viewer.set_sensor_indexes(association_indexes, graph_colors)
        self.association_indexes = association_indexes
        self.update_graph()

    def on_velocity_visibility_changed(self, state):
        self.velocity_visibility = not state
        self.update_graph()

    def on_run_timeline_clicked(self, run_timeline: bool):
        view: PlateTimelineView = self.view
        model: PlateTimelineModel = self.model
        model.is_running = run_timeline
        if run_timeline:
            model.get_camera_setting()
            view.update_lb_camera_settings()

            timeline: Timeline = model.timeline
            timeline.init_plate_info(model.snapshot_instance)
            QTimer.singleShot(0, self.take_snapshot)

    def take_snapshot(self):
        if not self.model.is_running:
            return

        view: PlateTimelineView = self.view
        image_viewer: ImageViewerController = view.image_viewer

        model: PlateTimelineModel = self.model
        timeline: Timeline = model.timeline
        snapshot_instance: Snapshot = model.snapshot_instance

        if timeline.current_count >= timeline.end_count:
            model.is_running = False
            image_viewer.switch_running_timeline(False)
            view.update_lb_interval_info()
            return

        QTimer.singleShot(timeline.current_interval * 1000, self.take_snapshot)

        image_viewer.take_snapshot()
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
