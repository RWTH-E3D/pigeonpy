import pandas as pd
import numpy as np


class Calculator(object):
    """Every conducted LCIA holds one Calculator object and calculation input (file) that is given during initialization.
    """
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

        calc_df = self.calc_in.get_calculation_df_for_partitions(*partitions)

        dataset_objects = []
        for index, row in calc_df.iterrows():
            dataset_object = epd_datamanager.load_epd(row['#uuid'], row['#scenario'])
            dataset_object *= row['#amount']
            dataset_object = self.calculate_replacements(
                dataset_object,
                observation_period,
                row['#replacement_cycle']
            )

            calculated_result_row = {
                'epd_dataset': dataset_object,
                'subset_name': row['subset_name']
            }
            dataset_objects.append(calculated_result_row)

        calculated_df = pd.DataFrame(dataset_objects, columns=['epd_dataset', 'subset_name'])
        calculated_series = calculated_df.groupby(['subset_name'], dropna=False)['epd_dataset'].sum()

        for index, dataset in calculated_series.items():
            dataset.name = str(index)

        return calculated_series

    @staticmethod
    def calculate_replacements(dataset_object, observation_period, replacement_cycle):
        """If replacements are specified in the input_csv for the given dataset_object, this method first calculates the
        amount of replacements based on the observation_period specified in the study. The divided number is rounded to
        the next bigger integer and subtracted by 1.
        E.g.: replacements = np.ceil(observation_period / replacement_cycle) - 1 = np.ceil(50 / 20) - 1 = 2.0
        Then the EPD gets multiplied with (replacements + 1), so the initially installed object is included, and
        returned to the calculate() method.

        Parameters
        ----------
        dataset_object
        observation_period
        replacement_cycle

        Returns
        -------

        """
        if isinstance(replacement_cycle, (int, float)) and not pd.isna(replacement_cycle):
            replacements = np.ceil(observation_period / replacement_cycle) - 1

            dataset_object *= (replacements + 1)
            dataset_object.history.log_operation(
                f"Calculate component replacements: "
                f"{dataset_object.history.initial_name} += {replacements} * {dataset_object.history.initial_name}",
                replace_last=True
            )

            return dataset_object
        else:
            return dataset_object
