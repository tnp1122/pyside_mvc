from models.api import Item, Items


class Material(Item):
    pass


class Materials(Items):
    def set_items_with_json(self, json_str: str, json_key: str):
        super().set_items_with_json(json_str, json_key, item_type=Material)
