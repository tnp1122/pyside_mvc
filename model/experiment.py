from model import Item, Items


class Experiment(Item):
    pass


class Experiments(Items):
    def set_items_with_json(self, json_str: str, json_key: str):
        super().set_items_with_json(json_str, json_key, item_type=Experiment)
