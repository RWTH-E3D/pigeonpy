import pandas as pd
import numpy as np
from study.calculationinput import CalculationInput


def calculate(*partitions, calculation_input, epd_datamanager, observation_period, replacement_stage=None):
    """Method for subset based calculation of datasets

    Loads the datasets based on their epd_id, multiplies them with the value defined in the input csv and sums up
    every dataset with the same subset name.

    Parameters
    ----------
    *partitions: str
        The subset name(s) as strings according to which the calculation will be made
    calculation_input : CalculationInput
        Contains the parsed info of the input CSV file and is called to create and return the dataframe for calculation
    epd_datamanager: EpdDatamanager
        Instance of the EpdDatamanager containing the databases with Epd datasets for calculation
    observation_period: int
        Time horizon for the calculation used for calculating the component exchanges
    replacement_stage : str
        Abbreviation for the life cycle stage that is used to store replacement indicator values. E.g. stage 'b4'
        when using standard EN15804. If not specified, i.e. None, replacements are calculated by multiplying the
        whole dataset with the amount of replacements.

    Returns
    ----------
    calculated_df: pd.Series
        Contains the subset or subset combination as index and the associated calculation result in the form
        of an EpdDataset object
    """

    calc_df = calculation_input.get_calculation_df_for_partitions(*partitions)

    dataset_objects = []
    for row in calc_df.itertuples(index=False):
        pass
        dataset_object = epd_datamanager.load_epd(row.epd_id, row.scenario)
        dataset_object *= row.amount
        replacements = calculate_replacements(
            observation_period,
            row.replacement_cycle
        )
        dataset_object.replace(replacements, replacement_stage=replacement_stage)

        calculated_result_row = {
            'epd_dataset': dataset_object,
            'subset_name': row.subset_name
        }
        dataset_objects.append(calculated_result_row)

    calculated_df = pd.DataFrame(dataset_objects, columns=['epd_dataset', 'subset_name'])
    calculated_series = calculated_df.groupby(['subset_name'], dropna=False)['epd_dataset'].sum()

    for index, dataset in calculated_series.items():
        dataset.name = str(index)

    return calculated_series


def calculate_replacements(observation_period, replacement_cycle):
    """If replacements are specified in the input_csv for the given dataset_object, this method first calculates the
    amount of replacements based on the observation_period specified in the study. The divided number is rounded to
    the next bigger integer and subtracted by 1.
    E.g.: replacements = np.ceil(observation_period / replacement_cycle) - 1 = np.ceil(50 / 20) - 1 = 2.0
    If replacements are specified, the calculated replacements are returned, otherwise 0 is returned.

    Parameters
    ----------
    observation_period : Int
        The period specified when creating the study.
    replacement_cycle : Int
        replacement_cycle column value defined in input_csv

    Returns
    -------
    replacements : int
        Either the number of replacements, if a replacement_cycle is specified in the input or 0.
    """
    if isinstance(replacement_cycle, (int, float)) and not pd.isna(replacement_cycle):
        replacements = np.ceil(observation_period / replacement_cycle) - 1
        return replacements
    else:
        replacements = 0
        return replacements


