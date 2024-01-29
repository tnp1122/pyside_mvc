from ui.common import BaseController
from ui.tabs.experiment.explorer import ExplorerModel, ExplorerView


class ExplorerController(BaseController):
    def __init__(self, parent=None):
        super().__init__(ExplorerModel, ExplorerView, parent)

    def init_controller(self):
        super().init_controller()
        self.update_tree_view()

    def update_tree_view(self):
        data = {
            'fish care': {
                '조합 1': {
                    'Cr_230926': ['8H', '12H'],
                    'FE_230422': ['8H'],
                },
                '조합 2': {
                    'Mn_220222': ['8H', '12H'],
                    'DDDDD_231212': ['8H']
                },
                '조합 3': {
                    'Cu_240115': ['4H', '8H', '12H']
                }
            }
        }
        self.view.tree.set_tree(data)


def main():
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    widget = ExplorerController()
    widget.view.show()
    app.exec()


if __name__ == "__main__":
    main()
