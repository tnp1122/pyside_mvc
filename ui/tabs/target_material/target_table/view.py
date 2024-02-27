from PySide6.QtWidgets import QHeaderView

from ui.common import BaseTableWidgetView


class TargetTableView(BaseTableWidgetView):
    experiment_id = -1

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        headers = ["타겟"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def update_experiment_id(self, experiment_id):
        self.experiment_id = experiment_id
