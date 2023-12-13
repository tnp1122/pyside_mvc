class MaskDistrictModel:
    def __init__(self):
        self._area_x = 100
        self._area_y = 100
        self._area_width = 1000
        self._area_height = 600
        self._direction = 1     # 0 = horizontal, 1 = vertical
        self._rotation = 0
        self._border_width = 10

        self._additive_axes = [42 + i * 83 for i in range(12)]
        self._solvent_axes = [37 + i * 75 for i in range(8)]
        self._axis_head_width = 50
        self._axis_head_height = 50

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

    @property
    def axis_head_width(self):
        return self._axis_head_width

    @property
    def axis_head_height(self):
        return self._axis_head_height

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

    @axis_head_width.setter
    def axis_head_width(self, width):
        self._axis_head_width = width

    @axis_head_height.setter
    def axis_head_height(self, height):
        self._axis_head_height = height
