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

        self.mouse = Mouse.NORMAL
        self.status = Status.NORMAL
        self.trigger = Trigger.DEACTIVATE

        self.resize_origin = None
        self.additive_axes_origin = None
        self.solvent_axes_origin = None

        self.view.scene.mouse_moved_signal.connect(self.on_mouse_moved)
        self.view.scene.mouse_pressed_signal.connect(self.on_mouse_pressed)
        self.view.scene.mouse_released_signal.connect(self.on_mouse_released)

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
        if self.mouse == Mouse.TOP or self.mouse == Mouse.BOTTOM:
            self.view.setCursor(Qt.SizeVerCursor)
        elif self.mouse == Mouse.LEFT or self.mouse == Mouse.RIGHT:
            self.view.setCursor(Qt.SizeHorCursor)
        elif self.mouse == Mouse.BOTTOM_RIGHT_LOT:
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
        print(event)
        if self.status == Status.NORMAL:
            self.check_mouse_position(event)

        elif self.status == Status.RESIZE:
            self.resize(event)

        # elif self.status == Status.ROTATE:
        #     self.rotate(event)

    def on_mouse_pressed(self, event):
        if self.mouse == Mouse.TOP or self.mouse == Mouse.BOTTOM or self.mouse == Mouse.LEFT or self.mouse == Mouse.RIGHT:
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
        self.mouse = Mouse.NORMAL
        self.status = Status.NORMAL
        self.trigger = Trigger.DEACTIVATE
        self.resize_origin = None
        self.additive_axes_origin = None
        self.solvent_axes_origin = None

    def check_mouse_position(self, event):
        mouse_x, mouse_y = event.scenePos().x(), event.scenePos().y()

        rect = self.get_scene_rect(self.border.mask_area)
        left, right, top, bottom = rect.left(), rect.right(), rect.top(), rect.bottom()

        self.mouse = Mouse.NORMAL

        if left < mouse_x < right:
            if top - 50 < mouse_y < top:
                self.mouse = Mouse.TOP
            elif bottom < mouse_y < bottom + 50:
                self.mouse = Mouse.BOTTOM

        # 좌표상 top 부분이 수치가 낮으므로 유의
        if top < mouse_y < bottom:
            if left - 50 < mouse_x < left:
                self.mouse = Mouse.LEFT
            elif right < mouse_x < right + 50:
                self.mouse = Mouse.RIGHT

        if (right < mouse_x < right + 50) and (bottom < mouse_y < bottom + 50):
            self.mouse = Mouse.BOTTOM_RIGHT_LOT

        self.set_mouse_cursor()

    def resize(self, event):
        mouse_x, mouse_y = event.scenePos().x(), event.scenePos().y()

        scene_rect = self.resize_origin
        area = self.border.mask_area.rect()

        adjust = 0

        if self.mouse == Mouse.TOP:
            adjust = scene_rect.top() - mouse_y
        elif self.mouse == Mouse.BOTTOM:
            adjust = mouse_y - scene_rect.bottom()
        elif self.mouse == Mouse.LEFT:
            adjust = scene_rect.left() - mouse_x
        elif self.mouse == Mouse.RIGHT:
            adjust = mouse_x - scene_rect.right()

        if self.trigger == Trigger.DEACTIVATE:
            if abs(adjust) < 10:
                return
            else:
                self.trigger = Trigger.ACTIVATE

        width = area.width()
        height = area.height()
        x = area.x()
        y = area.y()
        diff = 0  # x 또는 y 좌표 변화량

        if self.mouse == Mouse.TOP:
            height = scene_rect.height() + adjust
            diff = height - self.model.area_height
            self.model.area_y -= diff
            y = self.model.area_y

        elif self.mouse == Mouse.BOTTOM:
            height = scene_rect.height() + adjust

        elif self.mouse == Mouse.LEFT:
            width = scene_rect.width() + adjust
            diff = width - self.model.area_width
            self.model.area_x -= diff
            x = self.model.area_x

        elif self.mouse == Mouse.RIGHT:
            width = scene_rect.width() + adjust

        self.model.area_width = width
        self.model.area_height = height
        self.border.mask_area.setRect(x, y, width, height)
        if self.mouse == Mouse.TOP or self.mouse == Mouse.BOTTOM:
            for axis in self.border.additive_axes:
                axis.set_height(height, diff)
                self.set_axes(adjust)
        elif self.mouse == Mouse.LEFT or self.mouse == Mouse.RIGHT:
            for axis in self.border.solvent_axes:
                axis.set_height(width, diff)
                self.set_axes(adjust, False)

    def set_axes(self, adjust, is_vertical=True):
        if self.mouse == Mouse.TOP or self.mouse == Mouse.BOTTOM:
            size = self.resize_origin.height()
            axes = self.solvent_axes_origin
        elif self.mouse == Mouse.LEFT or self.mouse == Mouse.RIGHT:
            size = self.resize_origin.width()
            axes = self.additive_axes_origin
        else:
            return

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

        if self.mouse == Mouse.TOP or self.mouse == Mouse.BOTTOM:
            self.model.solvent_axes = new_axes
            new_axes = [self.model.area_y + axis for axis in new_axes]
        else:
            self.model.additive_axes = new_axes
            new_axes = [self.model.area_x + axis for axis in new_axes]

        self.border.set_interval(new_axes, is_vertical)

    # def rotate(self, event):
    #     x2, y2 = event.scenePos().x(), event.scenePos().y()
    #     o2 = math.atan((y2 - self.y0) / (x2 - self.x0))
    #     angle = (o2 - self.o1) * 180/math.pi
    #     self.border.setRotation(angle)
