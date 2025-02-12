from epd.epddataset.epddataset import EpdDataset
import numpy as np


class OtherDataset(EpdDataset):

    environmental_indicators = []
    life_cycle_stages = []
    stages_and_indicators_loaded = False  # Nicht nötig, da mehrere Instanzen von OtherDataset erstellt werden können mit unterschiedlichen stages und indicators
    def __init__(self, used_standard, used_stages=None, used_indicators=None):

        super().__init__()
        self.data = np.ndarray
        if used_standard == "A1" or used_standard == "A2":
            self.used_standard = used_standard
        else:
            raise Exception("The used standard can only be 'A1' or 'A2'")
        self.used_stages = used_stages
        self.used_indicators = used_indicators

        if not OtherDataset.stages_and_indicators_loaded:
            EpdDataset._set_indicators_and_stages(self,
                                                  indicator_list=self.used_indicators,
                                                  stages_list=self.used_stages)
            OtherDataset.stages_and_indicators_loaded = True

    def load_data_from_dataset(self, dataset_object):
        life_cycle_indices = [dataset_object.life_cycle_stages.index(stage) for stage in self.life_cycle_stages]
        environmental_indices = [dataset_object.environmental_indicators.index(indicator) for indicator in
                                 self.environmental_indicators]

        # Uses numpy advanced indexing to extract the desired subset
        self.data = dataset_object.data[np.ix_(environmental_indices, life_cycle_indices)]

