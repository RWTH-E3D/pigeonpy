from logic.epddataset.en15804A1dataset import En15804A1Dataset
from logic.epddataset.en15804A2dataset import En15804A2Dataset
import pandas as pd
from pathlib import Path

# Löschen falls übergeben wird siehe calculate Funktion
from data.dataclass import DataClass


class Calculator(object):
    def __init__(self, calculation_input):
        self.calc_in = calculation_input

    def calculate(self, *categorizations, epd_datamanager):
        """Method for category based calculation of datasets

        Loads the datasets based on the UUIDs, multiplies them with the value defined in the input csv and sums up
        every dataset with the same category name.

        Parameters
        ----------
        *categorizations: str
            The category name(s) as strings according to which the calculation will be made

        Returns
        -------
        calculated_df: pd.Series
            Contains the category or category combination as index and the associated calculation result in the form
            of an EpdDataset object
        """

        calc_df = self.calc_in._select_by_categorization(*categorizations)
        dataset_objects = []
        for index, row in calc_df.iterrows():
            #Todo: Why is here a dummy dataclass hardcoded?
            dummy_dataclass = DataClass(used_standard='EN15804+A2', file_format='csv')
            if dummy_dataclass.used_standard == "EN15804+A1":
                dataset_object = En15804A1Dataset()
            else:
                dataset_object = En15804A2Dataset()

            dataset_object.load_lca_dataset(row['epd_uuid'], epd_datamanager)
            dataset_object *= row['value']

            calculated_result_row = {
                'epd_dataset': dataset_object,
                'category_name': row['category_name']
                # 'categorization': row['categorization_name']
            }
            dataset_objects.append(calculated_result_row)
        calculated_df = pd.DataFrame(dataset_objects, columns=['epd_dataset', 'category_name'])
        #Todo: design a result class for epd-Results, weighted and normalized results (and make it extentible?)
        calculated_df = calculated_df.groupby(['category_name'])['epd_dataset'].sum()  # now a series
        for index, dataset in calculated_df.items():
            dataset._name = str(index)

        return calculated_df

