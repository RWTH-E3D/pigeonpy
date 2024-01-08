from logic.epddataset.epddataset import EpdDataset
from data.dataclass import DataClass
from logic.environmentalindicator.environmentalindicator import EnvironmentalIndicator
from logic.lifecyclestage.lifecyclestage import LifeCycleStage
import numpy as np


class En15804A1Dataset(EpdDataset):
    environmental_indicators = []
    life_cycle_stages = []
    loaded = False

    @classmethod
    def set_indicators_and_stages(cls):
        tmp_dataclass = DataClass()
        indicators = list(tmp_dataclass.indicators_bind["indicators_en_15804_a1"])
        life_cycle_stages = list(tmp_dataclass.life_cycle_stages_bind["LifeCycleStages"])

        for indicator in indicators:
            new_indicator = EnvironmentalIndicator(abbreviation=indicator["abbreviation"], name=indicator["name"],
                                                   unit=indicator["unit"], description=indicator["description"])
            cls.environmental_indicators.append(new_indicator)

        for stage in life_cycle_stages:
            new_stage = LifeCycleStage(abbreviation=stage["abbreviation"], name=stage["name"],
                                       description=stage["description"])
            cls.life_cycle_stages.append(new_stage)

        cls.loaded = True
        del tmp_dataclass

    def __init__(self, environmental_indicator=None, life_cycle_stages=None):

        super().__init__()
        self._data = np.full((25, 18), 0.0)
        if not self.loaded:
            En15804A1Dataset.set_indicators_and_stages()

    def load_lca_dataset(self, given_lca_id, data_class):

        lca_data_bind = data_class.lca_data_bind

        # Following only for json, probably not suitable for csv or xml
        if given_lca_id in lca_data_bind.keys():
            lca_dataset_bind = lca_data_bind[given_lca_id]
            self.epd_data_id = given_lca_id
            self._name = lca_dataset_bind["name"]
            self.ref_flow_unit = lca_dataset_bind["ref_flow"]["unit"]
            self.ref_flow_value = lca_dataset_bind["ref_flow"]["value"]
        else:
            print(f"No dataset for given lca id '{given_lca_id}' was found. Please enter a valid lca id.")
            return

        # to get a callable index
        indicators = list(data_class.indicators_bind["indicators_en_15804_a1"])
        life_cycle_stages = list(data_class.life_cycle_stages_bind["LifeCycleStages"])

        for indicator_index, indicator in enumerate(indicators):
            if indicator["abbreviation"] in lca_dataset_bind.keys():
                for stage_index, life_cycle_stage in enumerate(life_cycle_stages):
                    if life_cycle_stage["abbreviation"] in lca_dataset_bind[indicator["abbreviation"]]:
                        self._data[indicator_index][stage_index] = float((lca_dataset_bind[indicator["abbreviation"]]
                                                                         [life_cycle_stage["abbreviation"]]))
