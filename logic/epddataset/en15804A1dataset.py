from logic.epddataset.epddataset import EpdDataset
from data.dataclass import DataClass
from logic.environmentalindicator.environmentalindicator import EnvironmentalIndicator
from logic.lifecyclestage.lifecyclestage import LifeCycleStage
import numpy as np


def assign_indicators():
    tmp_dataclass = DataClass()
    indicator_list = []
    indicators = list(tmp_dataclass.indicators_bind["indicators_en_15804_a1"])
    for indicator in indicators:
        new_indicator = EnvironmentalIndicator(abbreviation=indicator["abbreviation"], name=indicator["name"],
                                               unit=indicator["unit"], description=indicator["description"])
        indicator_list.append(new_indicator)
    del tmp_dataclass
    return indicator_list


def assign_life_cycle_stages():
    tmp_dataclass = DataClass()
    life_cycle_stage_list = []
    life_cycle_stages = list(tmp_dataclass.life_cycle_stages_bind["LifeCycleStages"])
    for stage in life_cycle_stages:
        new_stage = LifeCycleStage(abbreviation=stage["abbreviation"], name=stage["name"],
                                   description=stage["description"])
        life_cycle_stage_list.append(new_stage)
    del tmp_dataclass
    return life_cycle_stage_list


class En15804A1Dataset(EpdDataset):
    environmental_indicators = assign_indicators()
    life_cycle_stages = assign_life_cycle_stages()

    def __init__(self, environmental_indicator=None, life_cycle_stages=None):

        super().__init__()
        self._data = np.full((25, 17), 0.0)

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
