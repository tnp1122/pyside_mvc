from functools import partial

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QHBoxLayout, QVBoxLayout


class MileStone(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid black;
                border-radius: 14px;
                padding: 5px 10px;
            }

            QPushButton:checked {
                background-color: #5E6C80;
                border: 1px solid #5E6C80;
                color: white;
            }
        """)


class MileStoneRadio(QWidget):
    selected = Signal(int)

    def __init__(self, texts, axis=1, parent=None):
        super().__init__(parent)

        self._selected_idx = 0

        if axis:
            lyt = QHBoxLayout(self)
        else:
            lyt = QVBoxLayout(self)

        from ui import MileStone
        self.stones = []
        for idx, text in enumerate(texts):
            mile_stone = MileStone(text)
            mile_stone.clicked.connect(partial(self.on_selected, idx))
            self.stones.append(mile_stone)
            lyt.addWidget(self.stones[idx])

        lyt.addStretch()
        self.stones[self._selected_idx].setChecked(True)

    @property
    def selected_idx(self):
        return self._selected_idx

    @selected_idx.setter
    def selected_idx(self, idx):
        self._selected_idx = idx

    def on_selected(self, idx):
        if idx == self.selected_idx:
            self.stones[idx].setChecked(True)
            return

        self.stones[self.selected_idx].setChecked(False)
        self.selected_idx = idx
        self.selected.emit(self.selected_idx)


def main():
    app = QApplication([])
    widget = MileStoneRadio(["마일스톤", "ㅇㅇ", "ㅇㅇㅇ"])
    widget.show()
    app.exec()


def milestone():
    app = QApplication([])
    widget = MileStone("마일스톤")
    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
    # milestone()
