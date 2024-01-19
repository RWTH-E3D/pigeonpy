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

    def __str__(self):
        row_labels = [indicators.abbreviation for indicators in self.environmental_indicators]
        col_labels = [stages.abbreviation for stages in self.life_cycle_stages]
        data_to_print = np.round(self._data, 4)
        print(f"\nUsed standard: {self.used_standard}")
        if self._name is not None:
            print(f"Dataset for '{self._name}':")
        else:
            print("Processed dataset")
        return f'{self.print__data(data_to_print, row_labels=row_labels, col_labels=col_labels)}'

    def load_lca_dataset(self, given_lca_id, data_class):

        if data_class.file_format == "teco_json":
            lca_dataset_input.load_lca_dataset_json(self, given_lca_id, data_class)
        elif data_class.file_format == "csv":
            lca_dataset_input.load_lca_dataset_csv(self, given_lca_id, data_class)
        else:
            print(f"Given input file format '{data_class.file_format}' for given id '{given_lca_id}' not available."
                  f"\nAvailable input formats: 'teco_json', 'csv'")

    # Test: methods to print the class in a representative way (could be moved to another module)
    def print__data(self, arr, row_labels=None, col_labels=None):  # print a 2d numpy array (maybe) or nested list
        max_chars = max([len(str(item)) for item in arr.flatten()])  # char number required to display any item in list
        rw = max([len(str(item)) for item in row_labels])  # max char width of row__labels
        string1 = str('%s %s' % (' ' * (rw + 1), ' '.join(self.format__1(max_chars, i) for i in col_labels)))
        for row_label, row in zip(row_labels, arr):
            string1 += "\n"
            string1 += str('%s [%s]' % (self.format__1(rw, row_label), ' '.join(self.format__1(max_chars, i) for i in row)))
        return string1

    @staticmethod
    def format__1(digits, num):
        if digits < len(str(num)):
            raise Exception("digits<len(str(num))")
        return ' ' * (digits - len(str(num))) + str(num)
