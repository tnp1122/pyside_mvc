from PySide6.QtCore import QObject, Signal

from models.snapshot import Snapshot, Timeline


class PlateTimelineModel(QObject):
    selected_associations_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_associations = []

        self.snapshot_instance = Snapshot()  # 마스킹 영역 설정용 스냅샷 객체
        self.timeline = []
        self.is_running = False

    def init_timeline_instance(self, timeline_name: str, target_name: str):
        self.timeline = Timeline(timeline_name, target_name)
