from collections import OrderedDict

from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QFont, QMouseEvent, QTransform
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QMenu

from ui.common import ImageButton, BaseScrollAreaView

from util import local_storage_manager as lsm
from util import image_converter as ic


timeline_title = "연속촬영"


class TreeSignalData:
    def __init__(self, indexes: list, type: str = ""):
        self.indexes = indexes
        self.type = type


class ButtonAdd(ImageButton):
    clicked = Signal(QMouseEvent)
    timeline_clicked = Signal()
    snapshot_clicked = Signal()

    def __init__(self, image, size):
        super().__init__(image=image, size=size, padding=(2, 2, 0, 4))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.rect().contains(event.pos()):
            if event.button() == Qt.LeftButton:
                if event.modifiers() == Qt.NoModifier:
                    if event.type() == QEvent.MouseButtonRelease:
                        self.clicked.emit(event)

        super().mouseReleaseEvent(event)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        act_add_timeline = menu.addAction("새 연속촬영")
        act_add_snapshot = menu.addAction("새 플레이트")
        act_add_timeline.triggered.connect(self.timeline_clicked.emit)
        act_add_snapshot.triggered.connect(self.snapshot_clicked.emit)
        menu.exec(self.mapToGlobal(pos))


class ButtonExpand(ImageButton):
    def __init__(self, image, size, padding, parent=None):
        super().__init__(image=image, size=size, padding=padding, parent=parent)
        self.pixmap = ic.path_to_q_pixmap(image)
        self.direction = 0
        self.clicked.connect(self.rotate_icon)

    def rotate_icon(self):
        rotated_pixmap = self.pixmap
        if self.direction == 0:
            rotated_pixmap = self.pixmap.transformed(QTransform().rotate(270))
        self.setIcon(rotated_pixmap)
        self.direction = abs(self.direction - 1)


class TreeView(BaseScrollAreaView):
    margin = 4

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 수평 스크롤바 비활성화
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.show_timeline = True
        self.data = OrderedDict()
        self.root = TreeRow()

    def closeEvent(self, event):
        self.data = None
        self.root.close()
        self.deleteLater()

        super().closeEvent(event)

    def set_tree(self, data):
        self.root.clear()
        self.root.add_child(data)

        tree = QWidget()
        lyt = QVBoxLayout(tree)
        lyt.setContentsMargins(self.margin, self.margin, self.margin, self.margin)
        lyt.addWidget(self.root)
        lyt.addStretch()
        lyt.setAlignment(Qt.AlignTop)
        self.setWidget(tree)
        self.switch_visibility(self.show_timeline)

    def switch_visibility(self, show_timeline=True):
        self.show_timeline = show_timeline
        self.root.switch_visibility(show_timeline)


class TreeRow(QWidget):
    icon_size = 15
    font_size = 11

    add_signal = Signal(TreeSignalData)
    double_clicked_signal = Signal(TreeSignalData)
    remove_signal = Signal(TreeSignalData)

    def __init__(self, is_directory=True, parent=None, title="폴더 이름", level=0, index=-1):
        super().__init__()

        self.children = []
        self.is_expanded = True
        self.is_visible = True

        self.is_directory = is_directory
        self.parent = parent
        self.title = title
        self.level = level
        self.is_root = self.level == 0
        self.index = index

        self.init_view()

    def closeEvent(self, event):
        self.clear()
        self.deleteLater()

        super().closeEvent(event)

    def init_view(self):
        lyt = QVBoxLayout(self)
        lyt_title = QHBoxLayout()
        self.lyt_children = QVBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(0)

        lyt.addLayout(lyt_title)
        lyt.addLayout(self.lyt_children)

        if self.level == 0:
            return
        img_expand = lsm.get_static_image_path("expand_arrow.png")
        if self.is_directory:
            img_icon = lsm.get_static_image_path("icon_directory.png")
        else:
            if self.parent.title == timeline_title:
                img_icon = lsm.get_static_image_path("icon_graph.png")
            else:
                img_icon = lsm.get_static_image_path("icon_document.png")
        img_add = lsm.get_static_image_path("icon_add.png")

        icon_size = (self.icon_size, self.icon_size)
        self.btn_expand = ButtonExpand(image=img_expand, size=icon_size, padding=(2, 2, 2, 2))
        self.icon = ImageButton(image=img_icon, size=icon_size, padding=(2, 2, 2, 2))
        self.lb_title = QLabel(self.title)
        self.btn_add = ButtonAdd(image=img_add, size=(13, 13))
        if (self.level != 1 and self.level != 2 and self.level != 3) or (self.level == 3 and self.index == 0):
            self.btn_add.setVisible(False)

        font = QFont()
        font.setPointSize(self.font_size)
        self.lb_title.setFont(font)

        if self.is_directory:
            lyt_title.addWidget(self.btn_expand)
        else:
            padding = QWidget()
            padding.setFixedWidth(self.icon_size)
            lyt_title.addWidget(padding)

        lyt_title.addWidget(self.icon)
        lyt_title.addWidget(self.lb_title)
        lyt_title.addWidget(self.btn_add)
        lyt_title.addStretch()

        self.set_signal()

    def clear(self):
        for child in self.children:
            child.close()
        self.children = []

        layout = self.lyt_children
        while layout.count():
            lyt_child = layout.takeAt(0)
            while lyt_child.count():
                widget = lyt_child.takeAt(0).widget()
                widget.deleteLater()
                widget.close()

    def set_branch_visible(self, visible: bool) -> None:
        self.is_visible = visible
        super().setVisible(visible)

    def switch_visibility(self, show_timeline=True):
        if self.level == 3:
            if show_timeline:
                if self.title == timeline_title:
                    self.set_branch_visible(True)
                else:
                    self.set_branch_visible(False)
            else:
                if self.title == timeline_title:
                    self.set_branch_visible(False)
                else:
                    self.set_branch_visible(True)

        for child in self.children:
            child: TreeRow
            child.switch_visibility(show_timeline)

    def set_signal(self):
        self.icon.installEventFilter(self)
        self.lb_title.installEventFilter(self)
        self.lb_title.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lb_title.customContextMenuRequested.connect(self.show_snapshot_context_menu)
        self.btn_expand.clicked.connect(self.expand)
        self.btn_add.clicked.connect(lambda event: self.on_add_button_clicked(event))
        self.btn_add.timeline_clicked.connect(lambda: self.bubble_event("add_timeline"))
        self.btn_add.snapshot_clicked.connect(lambda: self.bubble_event("add_snapshot"))

    def get_expand_icon_degree(self):
        return 0 if self.is_expanded else 270

    def expand(self):
        self.is_expanded = not self.is_expanded

        for child in self.children:
            child.setVisible(self.is_expanded and child.is_visible)

    def add_child(self, child_value):
        is_directory = isinstance(child_value, dict)
        if is_directory:
            for index, (title, child_dict) in enumerate(child_value.items()):
                self.make_child(title, index, child_dict)
            return

        for index, title in enumerate(child_value):
            self.make_child(title, index)

    def make_child(self, title, index, child_dict=None):
        is_directory = child_dict is not None
        padding = QWidget()
        padding.setFixedWidth(self.icon_size)

        child = TreeRow(is_directory, self, title, self.level + 1, index)
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

        if event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.LeftButton:
                if self.level == 4:
                    if self.parent.title == timeline_title:
                        self.bubble_event("open_timeline")
                    else:
                        self.bubble_event("open_snapshot")
                else:
                    self.expand()

        return super().eventFilter(obj, event)

    def on_mouse_enter(self):
        style = "background-color: #D9D9D9;"
        self.lb_title.setStyleSheet(style)

    def on_mouse_leave(self):
        style = ""
        self.lb_title.setStyleSheet(style)

    def bubble_event(self, signal, index=None):
        indexes = index if index else []
        if self.parent:
            indexes.insert(0, self.index)
            self.parent.bubble_event(signal, indexes)
            return
        if signal == "add":
            self.add_signal.emit(TreeSignalData(indexes))
        elif signal == "add_timeline":
            self.add_signal.emit(TreeSignalData(indexes, "timeline"))
        elif signal == "add_snapshot":
            self.add_signal.emit(TreeSignalData(indexes, "snapshot"))
        elif signal == "open_timeline" or signal == "open_snapshot":
            self.double_clicked_signal.emit(TreeSignalData(indexes, signal))
        elif signal == "remove":
            self.remove_signal.emit(TreeSignalData(indexes))
        elif signal == "remove_timeline":
            self.remove_signal.emit(TreeSignalData(indexes, "timeline"))
        elif signal == "remove_snapshot":
            self.remove_signal.emit(TreeSignalData(indexes, "snapshot"))

    def show_snapshot_context_menu(self, pos):
        menu = QMenu(self)

        act_remove = menu.addAction("삭제")
        if self.level == 4:
            if self.parent.title == timeline_title:
                signal = "_timeline"
            else:
                signal = "_snapshot"
        else:
            signal = ""
        act_remove.triggered.connect(lambda: self.bubble_event("remove" + signal))
        menu.exec(self.lb_title.mapToGlobal(pos))

    def on_add_button_clicked(self, event):
        if self.level == 2:
            self.btn_add.show_context_menu(event.pos())
            return

        self.bubble_event("add")


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
        },
        'fish care2': {
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
