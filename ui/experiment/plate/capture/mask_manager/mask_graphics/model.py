class MaskGraphicsModel:
    def __init__(self):
        self._is_circle_visible = False

        self._area_x = 563
        self._area_y = 530
        self._area_width = 1406
        self._area_height = 945
        self._scened_x = self.area_x     # 좌표 이동시 scene의 좌표도 이동하므로 원점에서의 좌표가 필요함
        self._scened_y = self.area_y

        self._direction = 1  # 0 = horizontal, 1 = vertical
        self._rotation = 0
        self._border_width = 10

        additive_interval = self._area_width / 12
        solvent_interval = self._area_height / 8
        self._additive_axes = [additive_interval / 2 + i * additive_interval for i in range(12)]
        self._solvent_axes = [solvent_interval / 2 + i * solvent_interval for i in range(8)]
        self._circle_radius = 35

        self._border_threshold = 30

    def get_circle_mask_info(self):
        circle_mask_info = {
            "x": self.area_x,
            "y": self.area_y,
            "width": self.area_width,
            "height": self.area_height,
            "direction": self.direction,
            "roation": self.rotation,
            "additive_axes": self.additive_axes,
            "solvent_axes": self.solvent_axes,
            "radius": self.circle_radius
        }
        return circle_mask_info

    @property
    def is_circle_visible(self):
        return self._is_circle_visible

    @property
    def area_x(self):
        return self._area_x

    @property
    def area_y(self):
        return self._area_y

    @property
    def area_width(self):
        return self._area_width

    @property
    def area_height(self):
        return self._area_height

    @property
    def scened_x(self):
        return self._scened_x

    @property
    def scened_y(self):
        return self._scened_y

    @property
    def direction(self):
        return self._direction

    @property
    def rotation(self):
        return self._rotation

    @property
    def border_width(self):
        return self._border_width

    @property
    def additive_axes(self):
        return self._additive_axes

    @property
    def solvent_axes(self):
        return self._solvent_axes

    @property
    def circle_radius(self):
        return self._circle_radius

    @property
    def border_threshold(self):
        return self._border_threshold

    @is_circle_visible.setter
    def is_circle_visible(self, value):
        self._is_circle_visible = value

    @area_x.setter
    def area_x(self, x):
        self._area_x = x

    @area_y.setter
    def area_y(self, y):
        self._area_y = y

    @area_width.setter
    def area_width(self, width):
        self._area_width = width

    @area_height.setter
    def area_height(self, height):
        self._area_height = height

    @scened_x.setter
    def scened_x(self, x):
        self._scened_x = x

    @scened_y.setter
    def scened_y(self, y):
        self._scened_y = y

    @direction.setter
    def direction(self, value):
        self._direction = value

    @rotation.setter
    def rotation(self, angle):
        self._rotation = angle

    @border_width.setter
    def border_width(self, width):
        self._border_width = width

    @additive_axes.setter
    def additive_axes(self, axes):
        self._additive_axes = axes

    @solvent_axes.setter
    def solvent_axes(self, axes):
        self._solvent_axes = axes

    def set_additive_axis(self, index, value):
        if not (0 <= index < len(self._additive_axes)):
            raise ValueError("올바른 인덱스를 입력하세요.")

        self._additive_axes[index] = value

    def set_solvent_axis(self, index, value):
        if not (0 <= index < len(self._solvent_axes)):
            raise ValueError("올바른 인덱스를 입력하세요.")

        self._solvent_axes[index] = value

    @circle_radius.setter
    def circle_radius(self, radius):
        self._circle_radius = radius

    @border_threshold.setter
    def border_threshold(self, threshold):
        self._border_threshold = threshold
