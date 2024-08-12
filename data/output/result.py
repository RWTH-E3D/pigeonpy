from logic.epddataset.otherdataset import OtherDataset
import data.output.lca_data_output as lca_data_output
import pandas as pd


class Result(object):
    def __init__(self, calculation_name, categorization, used_stages=None, used_indicators=None):
        self.calculation_name = calculation_name
        self.categorization = categorization
        self.calculated_dataframe = pd.Series

        self.used_stages = used_stages
        self.used_indicators = used_indicators


    def exclude_stages_and_indicators(self):
        # create new datasets with instances of OtherDataset and the information of the
        # datasets from the calculated dataframe for all datasets inside
        for index, dataset in self.calculated_dataframe.items():
            new_dataset = OtherDataset(used_standard=dataset.used_standard,
                                       used_stages=self.used_stages,
                                       used_indicators=self.used_indicators)
            new_dataset.load_data_from_dataset(dataset)
            self.calculated_dataframe[index] = new_dataset

        """Alternative"""
        # use the existing datasets and exclude the stages not needed by using the _get_index methods from
        # EpdDataset class


    def compare(self, other_result_to_compare_with):
        pass

    def normalize(self, data_for_normalization):
        pass

    def weight_results(self):
        pass
