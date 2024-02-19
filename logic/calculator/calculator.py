from logic.epddataset.en15804A1dataset import En15804A1Dataset
from logic.epddataset.en15804A2dataset import En15804A2Dataset
import pandas as pd

# Löschen falls übergeben wird siehe calculate Funktion
from data.dataclass import DataClass

class calculator(object):

    def __init__(self):
        self._calculation_table_header = ["calculation_id", "value", "epd_uuid", "epd_name", "comment"]
        dummy_data_calc = [[0,1, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""],
                           [1, 3, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""],
                           [2, 44, "c8835af8-44d2-47df-a833-8e823e6ee5cd", "", ""],
                           [3, 2, "9099dfdd-22a6-4dee-9b60-0e90701e9d99", "", ""]]
        self._calculation_table = pd.DataFrame(dummy_data_calc, columns=self._calculation_table_headers)

        dummy_data_cat = [[0, "1993", 0],
                          [1, "1993", 0],
                          [2, "1994", 0],
                          [3, "1995", 0]]
        self._category_name = ["calculation_id", "name", "categorization_id"]
        self._category_table = pd.DataFrame(dummy_data_cat, columns=self._category_name)

        dummy_data_calc = [0, "Jahr"]
        self._categorization_header = ["categorization_id", "name"]
        self._categorization_table = pd.DataFrame(dummy_data_calc, columns=self._categorization_header)

    def _select_by_categorization(self, *categorizations):
        result = df.query('A == 2')

        merged_df = self._calculation_table.merge(categorizations[0], on='category_id')


    def calculate(self, *categorizations):

        if len(categorizations) == 1:
            calc_df = self._select_by_categorization(categorizations[0])
        else:
            calc_df = self._select_by_categorization(categorizations[0], categorizations[1])

        dataset_objects = []
        for index, row in calc_df.iterrows():
            dummy_dataclass = DataClass(used_standard='A1', file_format='csv')
            if dummy_dataclass.used_standard == "A1":
                dataset_object = En15804A1Dataset()
            else:
                dataset_object = En15804A2Dataset()

            dataset_object.load_lca_dataset(row['epd_uuid'], data_class=dummy_dataclass)
            dataset_object *= row['value']

            calculated_result_row = {
                'epd_dataset': dataset_object,
                'category_name' : row['category_name'],
                'categorization': row['categorization_name']
            }
            dataset_objects.append(calculated_result_row)
        calculated_df = pd.DataFrame(dataset_objects, columns=['epd_dataset', 'category_name', 'categorization'])

        calculated_df = calculated_df.groupby('category_name')['epd_dataset'].sum()

        return calculated_df


