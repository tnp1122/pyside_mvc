import os

from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy

from ui.common import ImageButton, BaseScrollAreaView


class TreeView(BaseScrollAreaView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 수평 스크롤바 비활성화
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_tree(self, data):
        tree_root = TreeRow()
        tree_root.add_child(data)

        tree = QWidget()
        lyt = QVBoxLayout(tree)
        lyt.addWidget(tree_root)
        lyt.addStretch()
        lyt.setAlignment(Qt.AlignTop)
        self.setWidget(tree)


class TreeRow(QWidget):
    icon_size = 15
    font_size = 11

    clicked_signal = Signal(dict)

    def __init__(self, is_directory=True, parent=None, title="폴더 이름", level=0):
        super().__init__()

        self.children = []
        self.is_expended = True

        self.is_directory = is_directory
        self.parent = parent
        self.title = title
        self.level = level
        self.is_root = self.level == 0

        self.init_view()

    def init_view(self):
        lyt = QVBoxLayout(self)
        lyt_title = QHBoxLayout()
        self.lyt_children = QVBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(2)

        lyt.addStretch()
        lyt.addLayout(lyt_title)
        lyt.addLayout(self.lyt_children)
        lyt.addStretch()

        if self.level == 0:
            return
        img_expend = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  "../../static/image/expand_left.png")
        if self.is_directory:
            img_icon = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    "../../static/image/icon_directory.png")
        else:
            img_icon = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    "../../static/image/icon_document.png")
        img_add = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               "../../static/image/icon_add.png")

        icon_size = (self.icon_size, self.icon_size)
        self.btn_expend = ImageButton(image=img_expend, size=icon_size)
        self.icon = ImageButton(image=img_icon, size=icon_size)
        self.lb_title = QLabel(self.title)
        self.btn_add = ImageButton(image=img_add, size=icon_size)
        if (self.level != 1) and (self.level != 3):
            self.btn_add.setVisible(False)

        font = QFont()
        font.setPointSize(self.font_size)
        self.lb_title.setFont(font)

        if self.is_directory:
            lyt_title.addWidget(self.btn_expend)
        else:
            padding = QWidget()
            padding.setFixedWidth(self.icon_size)
            lyt_title.addWidget(padding)

        lyt_title.addWidget(self.icon)
        lyt_title.addWidget(self.lb_title)
        lyt_title.addWidget(self.btn_add)
        lyt_title.addStretch()

        style = "border: solid 2px red;"
        self.icon.setStyleSheet(style)

        self.set_signal()

    def set_signal(self):
        self.icon.installEventFilter(self)
        self.lb_title.installEventFilter(self)
        self.btn_expend.clicked.connect(self.expend)
        self.btn_add.clicked.connect(self.add_snapshot)

    def add_child(self, child_value):
        is_directory = isinstance(child_value, dict)
        if is_directory:
            for title, child_dict in child_value.items():
                self.make_child(title, child_dict)
            return

        for title in child_value:
            self.make_child(title=title)

    def make_child(self, title, child_dict=None):
        is_directory = child_dict is not None
        padding = QWidget()
        padding.setFixedWidth(self.icon_size)

        child = TreeRow(is_directory, self, title, self.level + 1)
        if is_directory:
            child.add_child(child_dict)
        self.children.append(child)

        lyt_child = QHBoxLayout()
        if not self.is_root:
            lyt_child.addWidget(padding)
        lyt_child.addWidget(child)
        self.lyt_children.addLayout(lyt_child)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.on_mouse_enter()

        if event.type() == QEvent.Leave:
            self.on_mouse_leave()

        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.on_click()

        if event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.LeftButton:
                self.expend()

        return super().eventFilter(obj, event)

    def on_mouse_enter(self):
        style = "background-color: #D9D9D9;"
        self.lb_title.setStyleSheet(style)

    def on_mouse_leave(self):
        style = ""
        self.lb_title.setStyleSheet(style)

    def on_click(self):
        if self.parent and self.parent.title:
            self.parent.on_child_click(self.title, self.level == 4)

    def on_child_click(self, title, from_bottom=False):
        info = {self.title: title}
        if self.parent and not self.parent.is_root:
            self.parent.on_child_click(info, from_bottom)

        if self.parent and self.parent.is_root:
            self.clicked_signal.emit(info)

    def expend(self):
        self.is_expended = not self.is_expended
        for child in self.children:
            child.setVisible(self.is_expended)

    def add_snapshot(self):
        print(f"[add] level: {self.level}")


def main():
    from PySide6.QtWidgets import QApplication

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

    app = QApplication([])
    widget = TreeView()
    widget.set_tree(data)

    widget.show()
    app.exec()


if __name__ == "__main__":
    main()
