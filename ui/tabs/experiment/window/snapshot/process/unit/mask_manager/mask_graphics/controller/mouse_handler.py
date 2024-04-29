from enum import Enum

from PySide6.QtCore import Qt, QRectF, QPointF

from model.snapshot import PlatePosition
from ui.tabs.experiment.window.snapshot.process.unit.mask_manager.mask_graphics.view.mask_area import MaskArea


class Mouse(Enum):
    NORMAL = 1
    TOP_LEFT = 2
    TOP = 3
    TOP_RIGHT = 4
    RIGHT = 5
    BOTTOM_RIGHT = 6
    BOTTOM = 7
    BOTTOM_LEFT = 8
    LEFT = 9
    TOP_LEFT_LOT = 10
    TOP_RIGHT_LOT = 11
    BOTTOM_RIGHT_LOT = 12
    BOTTOM_LEFT_LOT = 13


class Status(Enum):
    DEFAULT = 1
    MOVE = 2
    RESIZE = 3
    ROTATE = 4


class Trigger(Enum):
    DEACTIVATE = 1
    ACTIVATE = 2


class MouseHandler:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.model = main_controller.model
        self.snapshot = main_controller.snapshot
        self.view = main_controller.view
        self.area: MaskArea = self.view.scene.area

        self.mouse = [Mouse.NORMAL]
        self.status = Status.DEFAULT
        self.resize_trigger = Trigger.DEACTIVATE  # 리사이징할 때 최소 길이 만큼 움직였는지 확인 용

        self.origin_mouse = None
        self.origin_rect = None

        self.view.scene.mouse_pressed_signal.connect(self.on_mouse_pressed)
        self.view.scene.mouse_moved_signal.connect(self.on_mouse_moved)
        self.view.scene.mouse_released_signal.connect(self.on_mouse_released)

        self.border_threshold = 30

    def close(self):
        self.model = None
        self.snapshot = None
        self.view = None
        self.area = None
        self.mouse = None
        self.resize_origin = None
        self.additive_axes_origin = None
        self.solvent_axes_origin = None
        self.border_threshold = None

    def is_mouse_settable(self, check_vertical=True):
        if not self.model.is_border_adjustable:
            return False

        if check_vertical:
            return Mouse.TOP in self.mouse or Mouse.BOTTOM in self.mouse
        return Mouse.LEFT in self.mouse or Mouse.RIGHT in self.mouse

    def on_mouse_pressed(self, event):
        area = self.get_scene_rect(self.area)

        if self.is_mouse_settable(check_vertical=True) or self.is_mouse_settable(check_vertical=False):
            self.status = Status.RESIZE
            self.origin_mouse = event.scenePos()
            self.origin_rect = area
            return

        if area.contains(event.pos()):
            self.status = Status.MOVE
            self.origin_mouse = event.scenePos()
            self.origin_rect = area

        # elif self.mouse == Mouse.BOTTOM_RIGHT_LOT:
        #     self.border.set_movable(False)
        #     self.status = Status.ROTATE
        #     area_rect = self.border.mask_area.rect()
        #     self.x0, self.y0 = area_rect.center().x(), area_rect.center().y()
        #     x1, y1 = event.scenePos().x(), event.scenePos().y()
        #     self.o1 = math.atan((y1 - self.y0) / (x1 - self.x0))

    def on_mouse_moved(self, event):
        if self.status == Status.DEFAULT:
            self.check_mouse_position(event)
            return

        if self.status == Status.MOVE:
            origin_rect: QRectF = self.origin_rect
            origin_mouse: QPointF = self.origin_mouse
            new_mouse: QPointF = event.scenePos()

            x, y, width, height = origin_rect.getRect()
            dx = new_mouse.x() - origin_mouse.x()
            dy = new_mouse.y() - origin_mouse.y()
            new_rect = QRectF(x + dx, y + dy, width, height)

            plate: PlatePosition = self.snapshot.plate_position
            plate.set_position_with_qrect(new_rect)
            return

        if self.status == Status.RESIZE:
            origin_rect: QRectF = self.origin_rect
            origin_mouse: QPointF = self.origin_mouse
            new_mouse: QPointF = event.scenePos()

            dx, dy = 0, 0
            x, y, width, height = origin_rect.getRect()
            if Mouse.LEFT in self.mouse:
                dx = origin_mouse.x() - new_mouse.x()
                x -= dx
            elif Mouse.RIGHT in self.mouse:
                dx = new_mouse.x() - origin_mouse.x()
            if Mouse.TOP in self.mouse:
                dy = origin_mouse.y() - new_mouse.y()
                y -= dy
            elif Mouse.BOTTOM in self.mouse:
                dy = new_mouse.y() - origin_mouse.y()

            width += dx
            height += dy
            new_rect = QRectF(x, y, width, height)

            plate: PlatePosition = self.snapshot.plate_position
            plate.set_position_with_qrect(new_rect)

    def on_mouse_released(self, event):
        if self.status != Status.DEFAULT:
            self.snapshot.mask.update_mask()

            self.status = Status.DEFAULT
            self.origin_mouse = None
            self.origin_rect = None

    def set_mouse_cursor(self):
        if not self.model.is_border_adjustable:
            return

        if (Mouse.TOP in self.mouse and Mouse.LEFT in self.mouse) or (
                Mouse.BOTTOM in self.mouse and Mouse.RIGHT in self.mouse):
            self.view.setCursor(Qt.SizeFDiagCursor)
        elif (Mouse.TOP in self.mouse and Mouse.RIGHT in self.mouse) or (
                Mouse.BOTTOM in self.mouse and Mouse.LEFT in self.mouse):
            self.view.setCursor(Qt.SizeBDiagCursor)
        elif Mouse.TOP in self.mouse or Mouse.BOTTOM in self.mouse:
            self.view.setCursor(Qt.SizeVerCursor)
        elif Mouse.LEFT in self.mouse or Mouse.RIGHT in self.mouse:
            self.view.setCursor(Qt.SizeHorCursor)
        elif Mouse.BOTTOM_RIGHT_LOT in self.mouse:
            self.view.setCursor(Qt.CrossCursor)
        else:
            self.view.setCursor(Qt.ArrowCursor)

    def get_scene_rect(self, area) -> QRectF:
        left = area.scenePos().x() + area.rect().left()
        right = area.scenePos().x() + area.rect().right()
        top = area.scenePos().y() + area.rect().top()
        bottom = area.scenePos().y() + area.rect().bottom()

        return QRectF(QPointF(left, top), QPointF(right, bottom))

    def check_mouse_position(self, event):
        mouse_x, mouse_y = event.scenePos().x(), event.scenePos().y()
        rect = self.get_scene_rect(self.area)
        left, right, top, bottom = rect.left(), rect.right(), rect.top(), rect.bottom()
        self.mouse = [Mouse.NORMAL]

        if left - self.border_threshold < mouse_x < right + self.border_threshold:
            if top - self.border_threshold < mouse_y < top:
                self.mouse.append(Mouse.TOP)
            elif bottom < mouse_y < bottom + self.border_threshold:
                self.mouse.append(Mouse.BOTTOM)

        # 좌표상 top 부분이 수치가 낮으므로 유의
        if top - self.border_threshold < mouse_y < bottom + self.border_threshold:
            if left - self.border_threshold < mouse_x < left:
                self.mouse.append(Mouse.LEFT)
            elif right < mouse_x < right + self.border_threshold:
                self.mouse.append(Mouse.RIGHT)

        # if (right < mouse_x < right + 50) and (bottom < mouse_y < bottom + 50):
        #     self.mouse = [Mouse.BOTTOM_RIGHT_LOT]

        self.set_mouse_cursor()
