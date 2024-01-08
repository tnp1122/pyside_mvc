from PySide6.QtWidgets import QPushButton, QApplication


class ColoredButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #5E6C80;
                color: white;
                border: 0px;
                padding: 5px;
            }
        """)


def main():
    app = QApplication([])
    widget = ColoredButton("버튼")
    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
