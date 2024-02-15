from ui.tabs.material.tabs.tables.sample_table import SampleTableController


class MetalSampleTableController(SampleTableController):
    def __init__(self, parent=None):
        headers = ["시료 이름", "금속 종류", "제작 날짜", "사용"]
        args = {"tables": "metal", "headers": headers}
        super().__init__(parent, args)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = MetalSampleTableController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
