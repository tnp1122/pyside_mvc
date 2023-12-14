class MaskDistrictModel:
    def __init__(self):
        self._area_x = 500
        self._area_y = 1100
        self._area_width = 1000
        self._area_height = 600
        self._direction = 0  # 0 = horizontal, 1 = vertical
        self._rotation = 0
        self._border_width = 10

        additive_interval = self._area_width / 12
        solvent_interval = self._area_height / 8
        self._additive_axes = [additive_interval / 2 + i * additive_interval for i in range(12)]
        self._solvent_axes = [solvent_interval / 2 + i * solvent_interval for i in range(8)]

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
