from PySide6.QtCore import QTimer

from model.snapshot import Snapshot, Timeline
from ui.common import BaseController
from ui.common.image_viewer import ImageViewerController
from ui.tabs.experiment.window.timeline import PlateTimelineModel, PlateTimelineView
from ui.tabs.experiment.window.timeline.widgets.color_graph import ColorGraphController
from ui.tabs.experiment.window.timeline.widgets.select_combination_table import SelectCombinationTableController

str_run_complete = "타임라인 촬영 완료"


class PlateTimelineController(BaseController):
    def __init__(self, parent=None, args=None):
        combination_id = args["combination_id"]
        super().__init__(PlateTimelineModel, PlateTimelineView, parent, combination_id)

        self.target = args["target"]
        self.association_indexes = []

        model: PlateTimelineModel = self.model
        model.init_timeline_instance(args["timeline_path"], self.target.name)

        view: PlateTimelineView = self.view
        view.update_lb_interval_info()
        view.image_viewer.instance_initialized.connect(self.load_timeline)

        combination_table: SelectCombinationTableController = view.combination_table
        combination_table.display_associations_changed.connect(self.on_associations_changed)

    def init_controller(self):
        model: PlateTimelineModel = self.model
        self.view.set_model(model)

        super().init_controller()

        image_viewer: ImageViewerController = self.view.image_viewer
        image_viewer.run_timeline_clicked.connect(self.on_run_timeline_clicked)

    def load_timeline(self):
        view: PlateTimelineView = self.view
        model: PlateTimelineModel = self.model
        timeline: Timeline = model.timeline
        if timeline.load_timeline(model.snapshot_instance):
            self.update_graph()
            view.update_lb_interval_info(str_run_complete)

    def on_associations_changed(self, association_indexes: list):
        color_graph: ColorGraphController = self.view.graph
        graph_colors = color_graph.set_colors(len(association_indexes))

        image_viewer: ImageViewerController = self.view.image_viewer
        image_viewer.set_sensor_indexes(association_indexes, graph_colors)
        self.association_indexes = association_indexes
        self.update_graph()

    def update_graph(self):
        color_graph: ColorGraphController = self.view.graph
        timeline: Timeline = self.model.timeline

        color_graph.update_graph(*timeline.get_datas(self.association_indexes))

    def on_run_timeline_clicked(self, run_timeline: bool):
        model: PlateTimelineModel = self.model
        model.is_running = run_timeline
        if run_timeline:
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
            self.model.is_running = False
            view.update_lb_interval_info(str_run_complete)
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
