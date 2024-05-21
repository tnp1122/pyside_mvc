import numpy as np
import pandas as pd
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QVBoxLayout, QSizePolicy
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from ui.common import BaseWidgetView, BaseController


class ColorGraphModel:
    def __init__(self):
        pass


class ColorGraphView(BaseWidgetView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def init_view(self):
        super().init_view()

        self.fig = plt.Figure()
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = self.ax1.twinx()
        # self.fig.subplots_adjust(right=0.8)

        self.ax1.set_ylabel("distance")
        self.ax2.set_ylabel("velocity")
        self.canvas.draw()
        self.colors = []

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(0, 0, 0, 0)

        lyt.addWidget(self.canvas)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_style_sheet(self):
        self.setStyleSheet("border: 1px solid blue")

    def set_colors(self, num_display: int):
        new_colors = [plt.cm.rainbow(a) for a in np.linspace(0.0, 1.0, num_display)]
        self.colors.clear()
        self.colors.extend(new_colors)

    def update_graph(self, elapsed_times: list, datas: list[pd.DataFrame]):
        ax1 = self.ax1
        ax2 = self.ax2
        ax1.clear()
        ax2.clear()

        distance_datas = datas[0]
        velocity_datas = datas[1]
        for idx, (distance_column, velocity_column) in enumerate(zip(distance_datas, velocity_datas)):
            distance_values = distance_datas[distance_column].tolist()
            velocity_values = velocity_datas[velocity_column].tolist()
            ax1.plot(elapsed_times, distance_values, color=self.colors[idx], label=distance_column, linestyle="-")
            ax2.plot(elapsed_times, velocity_values, color=self.colors[idx], label=velocity_column, linestyle="--")

        ax1.set_ylabel("distance")
        ax2.set_ylabel("velocity")
        ax2.yaxis.set_label_position("right")
        ax2.yaxis.tick_right()

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines = lines1 + lines2
        labels = labels1 + labels2
        ax1.legend(lines, labels)

        self.canvas.draw()


class ColorGraphController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ColorGraphModel, ColorGraphView, parent)

    def init_controller(self):
        super().init_controller()

    def update_graph(self, elapsed_times: list, datas: list[pd.DataFrame]):
        view: ColorGraphView = self.view
        view.update_graph(elapsed_times, datas)

    def set_colors(self, num_display: int):
        view: ColorGraphView = self.view
        view.set_colors(num_display)

        return self.q_colors

    @property
    def colors(self):
        view: ColorGraphView = self.view
        return view.colors

    @property
    def q_colors(self):
        colors = self.colors
        q_colors = []
        for color in colors:
            q_colors.append(QColor.fromRgbF(*color))

        return q_colors


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ColorGraphController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
