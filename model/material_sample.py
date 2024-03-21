import json

from model import Item, Items


class MaterialSample(Item):
    def __init__(
            self,
            name: str = None,
            made_at: str = None,
            subject_type: str = None,
            subject: Item = None,
            id_: int = None
    ):
        super().__init__(id_, name)

        self.made_at = made_at
        self.subject_type = subject_type
        self.subject = subject

    def __str__(self):
        return f"{self.subject_type}Sample({self.to_dict()})"

    def to_dict(self):
        return {"id": self.id, "name": self.name, "made_at": self.made_at, self.subject_type: self.subject.to_dict()}

    def serialize(self):
        return {"id": self.id, "name": self.name, "made_at": self.made_at, self.subject_type: self.subject.id}


class MaterialSamples(Items):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_sample_items_with_json(
            self,
            subject_type: str,
            json_str: str,
            json_key: str
    ):
        self.clear()
        items = json.loads(json_str)[json_key]
        for item in items:
            subject = item[subject_type]
            subject_object = Item(subject["id"], subject["name"])
            sample_object = MaterialSample(item["name"], item["made_at"], subject_type, subject_object, item["id"])
            self.append(sample_object)

    def to_list(self):
        return [sample.to_dict() for sample in self]

    def serialize(self):
        return [sample.serialize() for sample in self]
