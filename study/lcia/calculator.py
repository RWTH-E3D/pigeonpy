import pandas as pd


def include_replacements(dataset_object, replacements):
    """Takes an EpdDataset object and the number of its replacements to calculate the product. The dataset gets
    multiplied by the number of replacements + 1."""
    if isinstance(replacements, float) and not pd.isna(replacements):
        dataset_object *= (replacements + 1)
        dataset_object.history.log_operation(
            f"Calculate component replacements: "
            f"{dataset_object.history.initial_name} += {replacements} * {dataset_object.history.initial_name}",
            replace_last=True
        )
    else:
        return


class Calculator(object):
    def __init__(self, calculation_input):
        self.calc_in = calculation_input

    def calculate(self, *partitions, epd_datamanager, observation_period):
        """Method for subset based calculation of datasets

        Loads the datasets based on the UUIDs, multiplies them with the value defined in the input csv and sums up
        every dataset with the same subset name.

        Parameters
        ----------
        *partitions: str
            The subset name(s) as strings according to which the calculation will be made
        epd_datamanager: EpdDatamanager
            Instance of the EpdDatamanager containing the databases with Epd datasets for calculation
        observation_period: int
            Time horizon for the calculation used for calculating the component exchanges

        Returns
        ----------
        calculated_df: pd.Series
            Contains the subset or subset combination as index and the associated calculation result in the form
            of an EpdDataset object
        """

        self.calc_in.calculate_component_replacements(observation_period)
        calc_df = self.calc_in.select_by_partition(*partitions)

        dataset_objects = []
        for index, row in calc_df.iterrows():
            dataset_object = epd_datamanager.load_epd(row['UUID'])
            dataset_object *= row['Amount']
            include_replacements(dataset_object, row['Replacements'])

            calculated_result_row = {
                'Epd_dataset': dataset_object,
                'Subset_name': row['Subset_name']
            }
            dataset_objects.append(calculated_result_row)

        calculated_df = pd.DataFrame(dataset_objects, columns=['Epd_dataset', 'Subset_name'])
        calculated_series = calculated_df.groupby(['Subset_name'], dropna=False)['Epd_dataset'].sum()

        for index, dataset in calculated_series.items():
            dataset.name = str(index)

        return calculated_series
