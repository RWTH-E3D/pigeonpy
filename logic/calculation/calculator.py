import pandas as pd



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
            dataset_object = epd_datamanager.load_epd(row['epd_uuid'])
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
            dataset.name = str(index)

        return calculated_df

