from logic.epddataset.en15804A1dataset import En15804A1Dataset
from logic.epddataset.en15804A2dataset import En15804A2Dataset
import pandas as pd
from pathlib import Path

# Löschen falls übergeben wird siehe calculate Funktion
from data.dataclass import DataClass


class Calculator(object):
    """Class for a category based calculation of datasets.

    Contains methods to import csv data as input for the calculation and the calculation itself

    Attributes
    ----------
    _calculation_header : list
        Column names for calculation df
    _calculation_df : pd.DataFrame
        Contains lca dataset UUIDs and their amount for the calculation
    _categorization_header: list
        Column names for categorization df
    _categorization_df: pd.DataFrame
        Contains the different categorizations for the calculation
    _category_header: list
        Column names for category df
    _category_df: pd.DataFrame
        Many to many connection of calculation df and categorization df (intermediate table with category names)
    """

    def __init__(self):
        self._calculation_header = ["calculation_id", "value", "epd_uuid", "epd_name", "comment"]
        dummy_data_calc = [[0, 1, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""],
                           [1, 3, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""],
                           [2, 44, "c8835af8-44d2-47df-a833-8e823e6ee5cd", "", ""],
                           [3, 2, "9099dfdd-22a6-4dee-9b60-0e90701e9d99", "", ""]]
        self._calculation_df = pd.DataFrame(dummy_data_calc, columns=self._calculation_header)

        dummy_data_cat = [[0, "1993", 0],
                          [1, "1993", 0],
                          [2, "1994", 0],
                          [3, "1995", 0],
                          [0, "test", 1],
                          [1, "test", 1],
                          [2, "test3", 1],
                          [3, "test4", 1],
                          [0, "Bauteil1", 2],
                          [1, "Bauteil1", 2],
                          [2, "Bauteil1", 2],
                          [3, "Bauteil2", 2]
                          ]
        self._category_header = ["calculation_id", "category_name", "categorization_id"]
        self._category_df = pd.DataFrame(dummy_data_cat, columns=self._category_header)

        dummy_data_catz = [[0, "Jahr"],
                           [1, "Typ"],
                           [2, "Bauteil"]]
        self._categorization_header = ["categorization_id", "categorization_name"]
        self._categorization_df = pd.DataFrame(dummy_data_catz, columns=self._categorization_header)

    def _select_by_categorization(self, *categorizations):
        """Method to create a dataframe for the calculation which additionally contains the category or category
        combination according to which the datasets will be calculated.

        Parameters
        ----------
        *categorizations: str
            The category names as strings according to which the calculation will be made

        Returns
        -------
        calc_df: pd.DataFrame
            Contains information for the calculation; UUIDs, amounts, category/ categories
        """

        if len(categorizations) == 1:
            categorization = categorizations[0]
            catz_df = self._categorization_df[self._categorization_df['categorization_name'] == categorization]
            cat_df = pd.merge(self._category_df, catz_df, on="categorization_id", how='inner')
            calc_df = pd.merge(self._calculation_df, cat_df, on="calculation_id", how='inner')
        else:
            categorization = ' '.join(categorizations)
            cat_df = self._category_df.merge(self._categorization_df, on='categorization_id')
            pivot_df = cat_df.pivot(index='calculation_id', columns='categorization_name',
                                    values='category_name').reset_index()
            pivot_df['category_name'] = pivot_df[list(categorizations)].apply(tuple, axis=1)
            calc_df = self._calculation_df.merge(pivot_df, on='calculation_id', how='left').fillna('')
            calc_df.insert(2, "categorization_name", categorization)

        return calc_df

    def import_calculation(self, path):
        """Method to set the class attributes (dataframes with calculation info, categorizations, categories)
        based on the input csv

        Parameters
        ----------
        path: str
            Path to the input csv file
        """

        import_df = (pd.read_csv(path, sep=',', encoding='ANSI'))
        import_df['UUID'] = import_df['UUID'].str.strip()

        catigorizations = [[idx, col] for idx, col in enumerate(import_df.columns[4:11])]
        categories = []
        calculations = []

        for idx, row in import_df.iloc[:, :4].iterrows():
            calculations.append([idx] + row.tolist())

        for col_idx, col_name in catigorizations:
            col_values = import_df.iloc[:, col_idx + 4]
            for idx, val in enumerate(col_values):
                categories.append([idx, val, col_idx])

        self._calculation_df = pd.DataFrame(calculations, columns=self._calculation_header)
        self._category_df = pd.DataFrame(categories, columns=self._category_header)
        self._categorization_df = pd.DataFrame(catigorizations, columns=self._categorization_header)

        """
        self._calculation_df = import_df
        self._calculation_df.insert(loc=0, column="calculation_id", value=self._calculation_df.index)
        self._calculation_df = self._calculation_df.rename(
            columns={list(import_df)[idx]: name for idx, name in enumerate(self._calculation_header)})
        self._calculation_df = self._calculation_df[self._calculation_header]



        #cat_df = import_df.iloc[:,[len_header:]]

        print(enumerate(self._calculation_header))

        """

    def calculate(self, *categorizations):
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

        if len(categorizations) == 1:
            calc_df = self._select_by_categorization(categorizations[0])
        else:
            calc_df = self._select_by_categorization(categorizations[0], categorizations[1])
        dataset_objects = []
        for index, row in calc_df.iterrows():
            dummy_dataclass = DataClass(used_standard='A2', file_format='csv')
            if dummy_dataclass.used_standard == "A1":
                dataset_object = En15804A1Dataset()
            else:
                dataset_object = En15804A2Dataset()

            dataset_object.load_lca_dataset(row['epd_uuid'], data_class=dummy_dataclass)
            dataset_object *= row['value']

            calculated_result_row = {
                'epd_dataset': dataset_object,
                'category_name': row['category_name']
                # 'categorization': row['categorization_name']
            }
            dataset_objects.append(calculated_result_row)
        calculated_df = pd.DataFrame(dataset_objects, columns=['epd_dataset', 'category_name'])

        calculated_df = calculated_df.groupby(['category_name'])['epd_dataset'].sum()  # now a series
        for index, dataset in calculated_df.items():
            dataset._name = str(index)

        return calculated_df

# test = Calculator()
# #print(test._select_by_categorization("Jahr", "Typ", "Bauteil")[["value", "epd_uuid", "category_name"]])
# test.import_calculation(Path(r"C:\Users\Cuypers\Documents\dynamic_lca_draft\data\input\inputdata\input_data_dynamic_csv_V2.CSV"))
# huhu = test.calculate("Category1", "Year Installation for components or occurence for consumption")
# print(huhu[("Technical building equipment", 1996)])
