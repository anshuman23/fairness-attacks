from .datamodule import Datamodule

class DrugConsumptionDatamodule(Datamodule):
    def __init__(self, data_dir: str, batch_size: int):
        super().__init__('drug2.npz', data_dir, batch_size)

    def get_sensitive_index(self) -> int:
        return 12

    def get_advantaged_value(self) -> object:
        return 1.0005306447706963
