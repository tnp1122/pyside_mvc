from ui.tabs.material.tabs.tables.sample_table import SampleTableController


class AdditiveSampleTableController(SampleTableController):
    def __init__(self, parent=None):
        headers = ["시료 이름", "첨가제 종류", "제작 날짜", "사용"]
        args = {"tables": "additive", "headers": headers}
        super().__init__(parent, args)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = AdditiveSampleTableController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
