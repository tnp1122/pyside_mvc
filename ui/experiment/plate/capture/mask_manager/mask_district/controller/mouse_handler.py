import math
from enum import Enum

from PySide6.QtCore import Qt, QRectF, QPointF


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
    NORMAL = 1
    RESIZE = 2
    ROTATE = 3


class Trigger(Enum):
    DEACTIVATE = 1
    ACTIVATE = 2


class MouseHandler:
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self._border = self.view.scene.border

        self.mouse = [Mouse.NORMAL]
        self.status = Status.NORMAL
        self.trigger = Trigger.DEACTIVATE

        self.resize_origin = None
        self.additive_axes_origin = None
        self.solvent_axes_origin = None

        self.view.scene.mouse_moved_signal.connect(self.on_mouse_moved)
        self.view.scene.mouse_pressed_signal.connect(self.on_mouse_pressed)
        self.view.scene.mouse_released_signal.connect(self.on_mouse_released)

        self.border_threshold = self.model.border_threshold

    @property
    def model(self):
        return self._model

    @property
    def view(self):
        return self._view

    @property
    def border(self):
        return self._border

    def set_mouse_cursor(self):
        if (Mouse.TOP in self.mouse and Mouse.LEFT in self.mouse) or (Mouse.BOTTOM in self.mouse and Mouse.RIGHT in self.mouse):
            self.view.setCursor(Qt.SizeFDiagCursor)
        elif (Mouse.TOP in self.mouse and Mouse.RIGHT in self.mouse) or (Mouse.BOTTOM in self.mouse and Mouse.LEFT in self.mouse):
            self.view.setCursor(Qt.SizeBDiagCursor)
        elif Mouse.TOP in self.mouse or Mouse.BOTTOM in self.mouse:
            self.view.setCursor(Qt.SizeVerCursor)
        elif Mouse.LEFT in self.mouse or Mouse.RIGHT in self.mouse:
            self.view.setCursor(Qt.SizeHorCursor)
        elif Mouse.BOTTOM_RIGHT_LOT in self.mouse:
            self.view.setCursor(Qt.CrossCursor)
        else:
            self.view.setCursor(Qt.ArrowCursor)

    def get_scene_rect(self, area):
        left = area.scenePos().x() + area.rect().left()
        right = area.scenePos().x() + area.rect().right()
        top = area.scenePos().y() + area.rect().top()
        bottom = area.scenePos().y() + area.rect().bottom()

        return QRectF(QPointF(left, top), QPointF(right, bottom))

    def on_mouse_moved(self, event):
        if self.status == Status.NORMAL:
            self.check_mouse_position(event)

        elif self.status == Status.RESIZE:
            self.resize(event)

        # elif self.status == Status.ROTATE:
        #     self.rotate(event)

    def on_mouse_pressed(self, event):
        if self.is_mouse_settable(check_vertical=True) or self.is_mouse_settable(check_vertical=False):
            self.border.set_movable(False)
            self.status = Status.RESIZE
            self.resize_origin = self.get_scene_rect(self.border.mask_area)
            self.additive_axes_origin = self.model.additive_axes
            self.solvent_axes_origin = self.model.solvent_axes

        # elif self.mouse == Mouse.BOTTOM_RIGHT_LOT:
        #     self.border.set_movable(False)
        #     self.status = Status.ROTATE
        #     area_rect = self.border.mask_area.rect()
        #     self.x0, self.y0 = area_rect.center().x(), area_rect.center().y()
        #     x1, y1 = event.scenePos().x(), event.scenePos().y()
        #     self.o1 = math.atan((y1 - self.y0) / (x1 - self.x0))

    def on_mouse_released(self, event):
        self.border.set_movable(True)
        self.status = Status.NORMAL
        self.trigger = Trigger.DEACTIVATE
        self.resize_origin = None
        self.additive_axes_origin = None
        self.solvent_axes_origin = None

    def check_mouse_position(self, event):
        mouse_x, mouse_y = event.scenePos().x(), event.scenePos().y()
        rect = self.get_scene_rect(self.border.mask_area)
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

    def resize(self, event):
        mouse_x, mouse_y = event.scenePos().x(), event.scenePos().y()

        scene_rect = self.resize_origin  # 원본의 실제 좌표
        area = self.border.mask_area.rect()  # 부모 상 위치 (0, 0)

        w_adjust = 0
        h_adjust = 0

        if Mouse.TOP in self.mouse:
            h_adjust = scene_rect.top() - mouse_y
        elif Mouse.BOTTOM in self.mouse:
            h_adjust = mouse_y - scene_rect.bottom()
        if Mouse.LEFT in self.mouse:
            w_adjust = scene_rect.left() - mouse_x
        elif Mouse.RIGHT in self.mouse:
            w_adjust = mouse_x - scene_rect.right()

        if self.trigger == Trigger.DEACTIVATE:
            if abs(w_adjust) < 3 and abs(h_adjust) < 3:
                return
            else:
                self.trigger = Trigger.ACTIVATE

        x = area.x()
        y = area.y()
        width = area.width()
        height = area.height()
        w_diff = 0
        h_diff = 0  # x 또는 y 좌표 변화량

        if Mouse.TOP in self.mouse:
            height = scene_rect.height() + h_adjust
            h_diff = height - area.height()
            y = y - h_diff

        elif Mouse.BOTTOM in self.mouse:
            height = scene_rect.height() + h_adjust

        if Mouse.LEFT in self.mouse:
            width = scene_rect.width() + w_adjust
            w_diff = width - area.width()
            x = x - w_diff

        elif Mouse.RIGHT in self.mouse:
            width = scene_rect.width() + w_adjust

        self.model.area_x = x
        self.model.area_y = y
        if self.model.direction == 0:
            self.model.area_width = width
            self.model.area_height = height
        else:
            self.model.area_width = height
            self.model.area_height = width

        self.border.setRect(x, y, width, height)
        self.border.mask_area.setRect(x, y, width, height)

        # 축 조정
        if self.is_mouse_settable(check_vertical=True) or self.is_mouse_settable(check_vertical=False):
            self.set_intervals(w_adjust, h_adjust)
            self.border.set_bar_height(height, h_diff, is_vertical=True)
            self.border.set_bar_height(width, w_diff, is_vertical=False)

        self.set_circles_center()

    def set_intervals(self, w_adjust, h_adjust):
        if self.model.direction == 0:
            vertical_axes = self.additive_axes_origin
            horizontal_axes = self.solvent_axes_origin
        else:
            vertical_axes = self.solvent_axes_origin
            horizontal_axes = self.additive_axes_origin

        if self.is_mouse_settable(check_vertical=True):
            size = self.resize_origin.height()
            axes = horizontal_axes
            new_axes = self.get_new_axes(size, axes, h_adjust)

            horizontal_axes = new_axes
            new_axes = [self.model.area_y + axis for axis in new_axes]
            self.border.set_intervals(new_axes, True)

        if self.is_mouse_settable(check_vertical=False):
            size = self.resize_origin.width()
            axes = vertical_axes
            new_axes = self.get_new_axes(size, axes, w_adjust)

            vertical_axes = new_axes
            new_axes = [self.model.area_x + axis for axis in new_axes]
            self.border.set_intervals(new_axes, False)

        if self.model.direction == 0:
            self.model.additive_axes = vertical_axes
            self.model.solvent_axes = horizontal_axes
        else:
            self.model.solvent_axes = vertical_axes
            self.model.additive_axes = horizontal_axes

    def get_new_axes(self, size, axes, adjust):
        intervals = [0] * len(axes)
        intervals[0] = axes[0]
        for i in range(1, len(axes)):
            intervals[i] = axes[i] - axes[i - 1]
        intervals.append(size - axes[-1])
        interval_ratios = [i / size for i in intervals]

        new_intervals = [interval + ratio * adjust for interval, ratio in zip(intervals, interval_ratios)]

        new_axes = [0] * (len(new_intervals) - 1)
        new_axes[0] = new_intervals[0]
        for i in range(1, len(new_intervals[:-1])):
            new_axes[i] = new_axes[i - 1] + new_intervals[i]

        return new_axes

    def is_mouse_settable(self, check_vertical=True):
        if check_vertical:
            return Mouse.TOP in self.mouse or Mouse.BOTTOM in self.mouse
        return Mouse.LEFT in self.mouse or Mouse.RIGHT in self.mouse

    def set_circles_center(self):
        pass

    # def rotate(self, event):
    #     x2, y2 = event.scenePos().x(), event.scenePos().y()
    #     o2 = math.atan((y2 - self.y0) / (x2 - self.x0))
    #     angle = (o2 - self.o1) * 180/math.pi
    #     self.border.setRotation(angle)
