import json


class NoItemError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Item:
    def __init__(self, item_id: int = None, item_name: str = None):
        self.id = item_id
        self.name = item_name

    def __str__(self):
        return f"{self.__class__.__name__}(id: {self.id}, name: {self.name})"

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Items(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(str(item) for item in self)})"

    def to_list(self):
        return [item.to_dict() for item in self]

    def set_items_with_json(self, json_str: str, json_key: str, item_type: type[Item] = Item):
        self.clear()
        items = json.loads(json_str)[json_key]
        for item in items:
            item_object = item_type(item["id"], item["name"])
            self.append(item_object)

    def item_from_id(self, item_id):
        for index, item in enumerate(self):
            if item.id == item_id:
                return index, item
        raise NoItemError("존재하지 않는 아이템 id입니다.")

    def item_from_name(self, item_name):
        for index, item in enumerate(self):
            if item.name == item_name:
                return index, item
        raise NoItemError("존재하지 않는 아이템 name입니다.")

    def item_id(self, index):
        return self[index].id

    def item_id_from_name(self, item_name):
        index, item = self.item_from_name(item_name)
        return index, item.id

    def item_name(self, index):
        return self[index].name

    def item_name_from_id(self, item_id):
        index, item = self.item_from_id(item_id)
        return index, item.name


def main():
    target_str = '''{"targets": [
    {"id": 1, "name": "t1"},
    {"id": 2, "name": "t2"},
    {"id": 3, "name": "t3"}
    ]
    }'''
    targets = Items()
    targets.set_items_with_json(target_str, "targets")

    index, target = targets.item_from_id(2)
    print(targets)
    print(target)
    print(index, target.name)
    index, target = targets.item_from_name("t1")
    print(index, target.id)

    print(targets.item_id(0))
    print(targets.item_name(0))


if __name__ == "__main__":
    main()
