from PySide6.QtWidgets import QApplication, QPushButton


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


def main():
    app = QApplication([])
    widget = MileStone("마일스톤")
    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
