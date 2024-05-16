from model.api import MaterialSample, MaterialSamples


class MetalSample(MaterialSample):
    pass


class MetalSamples(MaterialSamples):
    def set_items_with_json(self, json_str: str, json_key: str):
        return super().set_items_with_json(json_str, json_key, item_type=MetalSample)

    @property
    def using_metal_samples(self):
        from util.setting_manager import SettingManager
        setting_manager = SettingManager()
        use_metal_samples = setting_manager.get_use_metal_samples()

        samples = MetalSamples()
        for sample in self:
            sample: MetalSample
            if sample.id in use_metal_samples:
                samples.append(sample)
        return samples
