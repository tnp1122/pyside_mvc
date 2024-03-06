import numpy as np
from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, xyYColor, LabColor


class ColorDifferenceModel:
    def __init__(self):
        self.targets = []
        self.target_rgb_colors = [[]]

        self.target_index = 0
        self.control_index = 0
        self.color_types = ["rgb", "xyy", "lab"]
        self.color_index = 0

        self.base_headers = ["Target", "Target", "Target", "Control", "Control", "Control", "Color"]
        self.rgb_headers = ["R", "G", "B", "R", "G", "B", "Distance"]
        self.xyy_headers = ["x", "y", "Y", "x", "y", "Y", "Distance"]
        self.lab_headers = ["L", "a", "b", "L", "a", "b", "Distance"]

    def get_target_cmb_names(self):
        target_names = []
        for index, target in enumerate(self.targets):
            if index == self.control_index:
                continue
            target_names.append(target["name"])

        return target_names

    def get_headers(self, color_type="rgb"):
        if color_type == "xyy":
            sub_headers = self.xyy_headers
        elif color_type == "lab":
            sub_headers = self.lab_headers
        else:
            sub_headers = self.rgb_headers
        return [f"{base} {sub}" for base, sub in zip(self.base_headers, sub_headers)]

    def get_color_datas(self, color_type="rgb", target_index=None):
        if target_index is None:
            target_index = self.target_index
        control_index = self.control_index

        if color_type == "xyy":
            get_colors = self.get_xyy_colors
        elif color_type == "lab":
            get_colors = self.get_lab_colors
        else:
            get_colors = self.get_rgb_colors
        target_colors = get_colors(target_index)
        control_colors = get_colors(control_index)

        return target_colors, control_colors, self.get_color_differences(target_colors, control_colors)

    def get_target_index(self, target_name=None, target_id=None):
        if target_name:
            for index, target in enumerate(self.targets):
                if target["name"] == target_name:
                    return index

        if target_id:
            for index, target in enumerate(self.targets):
                if target["id"] == target_id:
                    return index

        return -1

    def get_selected_color_type(self):
        return self.color_types[self.color_index]

    def get_rgb_colors(self, target_index):
        pixmap_rgb_colors = self.target_rgb_colors[target_index]
        cell_rgb_colors = []

        row_count = len(pixmap_rgb_colors)
        column_count = len(pixmap_rgb_colors[0])
        for row in list(range(row_count - 1, -1, -1)):
            for column in range(column_count):
                cell_rgb_colors.append(pixmap_rgb_colors[row][column])

        return cell_rgb_colors

    def get_xyy_colors(self, target_index):
        target_rgb_colors = self.get_rgb_colors(target_index)
        xyy_colors = []

        for rgb in target_rgb_colors:
            normalized = [value / 255 for value in rgb]
            srgb = sRGBColor(*normalized)
            xyy = convert_color(srgb, xyYColor)
            xyy_colors.append([xyy.xyy_x, xyy.xyy_y, xyy.xyy_Y])

        return xyy_colors

    def get_lab_colors(self, target_index):
        target_rgb_colors = self.get_rgb_colors(target_index)
        lab_colors = []

        for rgb in target_rgb_colors:
            normalized = [value / 255 for value in rgb]
            srgb = sRGBColor(*normalized)
            lab = convert_color(srgb, LabColor)
            lab_colors.append([lab.lab_l, lab.lab_a, lab.lab_b])

        return lab_colors

    def get_color_differences(self, target_colors, control_colors):
        differences = []

        for target_color, control_color in zip(target_colors, control_colors):
            difference = round(np.sqrt(
                (target_color[0] - control_color[0]) ** 2 +
                (target_color[1] - control_color[1]) ** 2 +
                (target_color[2] - control_color[2]) ** 2
            ), 3)
            differences.append(difference)

        return differences
