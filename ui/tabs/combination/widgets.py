from PySide6.QtGui import QPainter, Qt, QPen, QFont
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QComboBox, QDialog

from ui.common import ColoredButton, RefreshButton


class BaseCell(QPushButton):
    solvent = {"id": -1, "name": ""}
    additive = {"id": -1, "name": ""}

    def __init__(self, text=None, parent=None):
        super().__init__(text, parent)

    def set_solvent(self, solvent=None):
        if solvent:
            self.solvent = solvent
        else:
            self.solvent = {"id": -1, "name": ""}

    def set_additive(self, additive=None):
        if additive:
            self.additive = additive
        else:
            self.additive = {"id": -1, "name": ""}


class Cell(BaseCell):
    index = -1

    style = "text-align: left; padding: 4px;"
    style_sensor = ""
    style_half = ""
    style_void = ""

    def __init__(self, index, text=None, parent=None):
        super().__init__(text, parent)

        self.index = index
        self._set_text()

    def _set_text(self):
        solvent = self.solvent["name"]
        additive = self.additive["name"]
        self.setText(f"{solvent}_{additive}")

        if solvent == "" and additive == "":
            self.setText("")
            self.setStyleSheet(self.style_void)
        elif solvent == "" or additive == "":
            self.setStyleSheet(self.style_half)
        else:
            self.setStyleSheet(self.style_sensor)

    def switch_style(self, editable=False):
        if editable:
            style_editable = self.style + "background-color: white; border: 1px solid black;"
            self.style_sensor = style_editable + "color: black; font-weight: bold;"
            self.style_half = style_editable + "color: #BBBBBB;"
            self.style_void = style_editable
        else:
            self.style_sensor = self.style + "background-color: #DDDDDD; border: 1px solid white;"
            self.style_void = self.style + "background-color: #F5F5F5; border: 1px solid white; color: white;"
            self.style_half = self.style_void

        self._set_text()

    def set_solvent(self, solvent=None):
        super().set_solvent(solvent)
        self._set_text()

    def set_additive(self, additive=None):
        super().set_additive(additive)
        self._set_text()


class Label(BaseCell):
    def __init__(self, index: int, digit=True, parent=None):
        if digit:
            text = str(index)
        else:
            text = chr(ord("A") + index)
        super().__init__(text, parent)

        style = "text-align: center; padding: 4px; background-color: white; border: 1px solid white;"
        self.setStyleSheet(style)


class LabelTitle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(60)

        lb_solvent = QLabel("용매")
        lb_additive = QLabel("첨가제")

        lyt_additive = QHBoxLayout()
        lyt_additive.addStretch()
        lyt_additive.addWidget(lb_additive)
        lyt_additive.setContentsMargins(0, 0, 0, 0)

        lyt = QVBoxLayout(self)
        lyt.addWidget(lb_solvent)
        lyt.addLayout(lyt_additive)
        lyt.setContentsMargins(0, 0, 0, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.width(), 0, 0, self.height())


class SelectSensorWidget(QDialog):
    x, y = -1, -1
    max_width_cmb = 125

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("센서 시료 선택")
        self.setFixedSize(280, 180)

        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        lb_title = QLabel("센서 시료 선택")
        lb_title.setFont(font)
        self.btn_refresh = RefreshButton()
        lyt_title = QHBoxLayout()
        lyt_title.addStretch()
        lyt_title.addWidget(lb_title)
        lyt_title.addWidget(self.btn_refresh)
        lyt_title.addStretch()

        self.lb_solvent = QLabel("용매")
        self.cmb_solvent = QComboBox()
        self.cmb_solvent.setFixedWidth(self.max_width_cmb)
        lyt_solvent = QHBoxLayout()
        lyt_solvent.addWidget(self.lb_solvent)
        lyt_solvent.addWidget(self.cmb_solvent)

        self.lb_additive = QLabel("첨가제")
        self.cmb_additive = QComboBox()
        self.cmb_additive.setFixedWidth(self.max_width_cmb)
        lyt_additive = QHBoxLayout()
        lyt_additive.addWidget(self.lb_additive)
        lyt_additive.addWidget(self.cmb_additive)

        self.btn_cancel = ColoredButton("취소", background_color="white", color="black")
        self.btn_cancel.clicked.connect(self.close)
        self.btn_confirm = ColoredButton("확인")
        lyt_btns = QHBoxLayout()
        lyt_btns.addWidget(self.btn_cancel)
        lyt_btns.addWidget(self.btn_confirm)

        lyt = QVBoxLayout(self)
        lyt.setSpacing(10)
        lyt.addLayout(lyt_title)
        lyt.addLayout(lyt_solvent)
        lyt.addLayout(lyt_additive)
        lyt.addLayout(lyt_btns)

        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def custom_exec(self, x, y):
        self.x, self.y = x, y
        self.exec()

    def closeEvent(self, event):
        self.x, self.y = -1, -1
        self.cmb_solvent.setCurrentIndex(0)
        self.cmb_solvent.setVisible(True)
        self.lb_solvent.setVisible(True)
        self.cmb_additive.setCurrentIndex(0)
        self.cmb_additive.setVisible(True)
        self.lb_additive.setVisible(True)
        super().closeEvent(event)

    def set_solvent_invisible(self):
        self.cmb_additive.setVisible(False)
        self.lb_additive.setVisible(False)

    def set_additive_invisible(self):
        self.cmb_solvent.setVisible(False)
        self.lb_solvent.setVisible(False)

    def set_cmb_solvent(self, solvents):
        self.cmb_solvent.clear()
        self.cmb_solvent.addItem("선택 안함")
        for solvent in solvents:
            self.cmb_solvent.addItem(solvent["name"])

    def set_cmb_additive(self, additives):
        self.cmb_additive.clear()
        self.cmb_additive.addItem("선택 안함")
        for additive in additives:
            self.cmb_additive.addItem(additive["name"])

    def set_selected_index(self, solvent_index=0, additive_index=0):
        self.cmb_solvent.setCurrentIndex(solvent_index)
        self.cmb_additive.setCurrentIndex(additive_index)

    def get_selected_index(self):
        solvent_index = self.cmb_solvent.currentIndex()
        additive_index = self.cmb_additive.currentIndex()
        return solvent_index, additive_index


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    # widget = Cell("cell")
    # widget = LabelTitle()
    widget = SelectSensorWidget()
    # widget = Label(1, False)
    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
