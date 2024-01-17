from logic.epddataset.epddataset import EpdDataset
from data.dataclass import DataClass
from logic.environmentalindicator.environmentalindicator import EnvironmentalIndicator
from logic.lifecyclestage.lifecyclestage import LifeCycleStage
import data.input.lca_dataset_input as lca_dataset_input
import numpy as np


class En15804A1Dataset(EpdDataset):
    environmental_indicators = []
    life_cycle_stages = []
    stages_and_indicators_loaded = False

    @classmethod
    def set_indicators_and_stages(cls):
        tmp_dataclass = DataClass()

        for indicator in tmp_dataclass.indicators_bind:
            new_indicator = EnvironmentalIndicator(abbreviation=indicator["abbreviation"], name=indicator["name"],
                                                   unit=indicator["unit"], description=indicator["description"])
            cls.environmental_indicators.append(new_indicator)

        for stage in tmp_dataclass.life_cycle_stages_bind:
            new_stage = LifeCycleStage(abbreviation=stage["abbreviation"], name=stage["name"],
                                       description=stage["description"])
            cls.life_cycle_stages.append(new_stage)

        cls.stages_and_indicators_loaded = True
        del tmp_dataclass

    def __init__(self):

        super().__init__()
        self._data = np.full((25, 18), 0.0)
        self.used_standard = "En15804+A1"
        if not self.stages_and_indicators_loaded:
            En15804A1Dataset.set_indicators_and_stages()

    def load_lca_dataset(self, given_lca_id, data_class):

        if data_class.file_format == "teco_json":
            lca_dataset_input.load_lca_dataset_json(self, given_lca_id, data_class)
        elif data_class.file_format == "csv":
            lca_dataset_input.load_lca_dataset_csv(self, given_lca_id, data_class)
        else:
            print(f"Given input file format '{data_class.file_format}' for given id '{given_lca_id}' not available."
                  f"\nAvailable input formats: 'teco_json', 'csv'")

