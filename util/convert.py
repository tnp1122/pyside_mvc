from collections import OrderedDict


def convert_to_ordered_dict(data):
    if isinstance(data, dict):
        ordered_dict = OrderedDict()
        for key, value in data.items():
            ordered_dict[key] = convert_to_ordered_dict(value)
        return ordered_dict
    elif isinstance(data, list):
        return [convert_to_ordered_dict(item) for item in data]
    else:
        return data
